interface StatusBadgeProps {
  status: "Critical" | "Low Stock" | "Healthy" | "Overstocked" | string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  let style = "bg-slate-100 text-slate-700 border-slate-200";

  switch (status?.toLowerCase()) {
    case "critical":
      style = "bg-rose-50 text-rose-700 border-rose-200";
      break;
    case "low stock":
      style = "bg-amber-50 text-amber-700 border-amber-200";
      break;
    case "healthy":
      style = "bg-emerald-50 text-emerald-700 border-emerald-200";
      break;
    case "overstocked":
      style = "bg-indigo-50 text-indigo-700 border-indigo-200";
      break;
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${style}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      {status}
    </span>
  );
}
