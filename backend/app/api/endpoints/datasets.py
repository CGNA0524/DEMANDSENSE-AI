import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.db.models import DatasetImport
from app.core.config import settings
from app.services.dataset_service import DatasetService
from app.schemas.dataset import (
    DatasetPreviewResponse, ColumnMapping, ImportCommitRequest,
    DatasetImportHistoryItem, ValidationSummary
)
from app.schemas.common import ApiResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024 # 50 MB

@router.post("/upload", response_model=ApiResponse[DatasetPreviewResponse])
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    file_path_obj = Path(file.filename or "")
    suffix = file_path_obj.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Secure file name to prevent directory traversal
    clean_filename = f"{uuid.uuid4().hex[:8]}_{file_path_obj.name}"
    target_path = settings.UPLOADS_DIR / clean_filename

    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {e}")

    try:
        preview = DatasetService.preview_dataset(target_path)
        return ApiResponse(
            success=True,
            message="File uploaded and preview generated successfully.",
            data=preview
        )
    except Exception as e:
        if target_path.exists():
            target_path.unlink()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error parsing file: {e}")

@router.post("/import", response_model=ApiResponse[ValidationSummary])
def import_dataset(request: ImportCommitRequest, db: Session = Depends(get_db)):
    # Prevent traversal
    file_name = Path(request.filename).name
    file_path = settings.UPLOADS_DIR / file_name

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Uploaded file '{file_name}' not found.")

    try:
        raw_df = DatasetService.read_dataframe(file_path)
        clean_df, summary = DatasetService.validate_and_prepare(raw_df, request.mapping)

        if not summary.is_valid:
            return ApiResponse(
                success=False,
                message="Dataset validation failed. Please review errors and correct column mappings.",
                data=summary
            )

        suffix = file_path.suffix.lower().replace(".", "")
        DatasetService.save_to_database(
            db=db,
            df=clean_df,
            filename=file_name,
            file_type=suffix,
            is_demo=False,
            summary=summary
        )

        return ApiResponse(
            success=True,
            message=f"Successfully imported {summary.valid_rows} records across {summary.detected_products_count} products.",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Import failed: {str(e)}")

@router.post("/load-demo", response_model=ApiResponse[ValidationSummary])
def load_demo_data(db: Session = Depends(get_db)):
    try:
        df = DatasetService.generate_synthetic_demo_dataset()
        summary = ValidationSummary(
            is_valid=True,
            total_rows=len(df),
            valid_rows=len(df),
            error_count=0,
            warning_count=0,
            detected_products_count=df["product_id"].nunique(),
            date_min=str(df["date"].min()),
            date_max=str(df["date"].max()),
            issues=[]
        )
        DatasetService.save_to_database(
            db=db,
            df=df,
            filename="synthetic_retail_demo_dataset.csv",
            file_type="synthetic",
            is_demo=True,
            summary=summary
        )
        return ApiResponse(
            success=True,
            message="Deterministic synthetic demo dataset (15 products, 180 days, seasonal & promotional patterns) loaded successfully.",
            data=summary
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load demo data: {e}")

@router.get("/history", response_model=ApiResponse[List[DatasetImportHistoryItem]])
def get_import_history(db: Session = Depends(get_db)):
    history = db.query(DatasetImport).order_by(desc(DatasetImport.created_at)).limit(25).all()
    items = [
        DatasetImportHistoryItem(
            id=h.id,
            filename=h.filename,
            file_type=h.file_type,
            row_count=h.row_count,
            valid_row_count=h.valid_row_count,
            error_count=h.error_count,
            warning_count=h.warning_count,
            is_demo=h.is_demo,
            status=h.status,
            created_at=h.created_at
        )
        for h in history
    ]
    return ApiResponse(success=True, message="Import history retrieved.", data=items)

@router.get("/template")
def download_sample_template():
    csv_content = (
        "date,product_id,product_name,category,store_id,units_sold,unit_price,unit_cost,inventory_on_hand,supplier_lead_time_days,promotion,discount,stockout_indicator\n"
        "2026-01-01,PROD-001,Wireless Ergonomic Mouse,Electronics,STORE-01,15,29.99,12.50,45,7,0,0.0,0\n"
        "2026-01-02,PROD-001,Wireless Ergonomic Mouse,Electronics,STORE-01,18,29.99,12.50,30,7,0,0.0,0\n"
        "2026-01-03,PROD-001,Wireless Ergonomic Mouse,Electronics,STORE-01,24,29.99,12.50,12,7,1,0.15,0\n"
        "2026-01-01,PROD-002,Organic Fairtrade Coffee 1kg,Grocery,STORE-01,35,22.00,9.80,80,5,0,0.0,0\n"
    )
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=demandsense_template.csv"}
    )
