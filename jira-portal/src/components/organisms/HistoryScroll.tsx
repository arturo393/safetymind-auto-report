import { Download, FileText, Trash2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { useQuery, useQueryClient } from "@tanstack/react-query";

async function fetchReports() {
  const res = await fetch("/api/reports/list");
  return res.json();
}

interface IndustrialAsset {
  name: string;
  size: string;
  date: string;
}

export function HistoryScroll() {
  const queryClient = useQueryClient();
  const { data: reports, isLoading } = useQuery<IndustrialAsset[]>({
    queryKey: ["reports"],
    queryFn: fetchReports,
  });

  const handleDownload = (filename: string) => {
    window.open(`/api/reports/download/${filename}`, "_blank");
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`¿Confirmar eliminación de ${filename}?`)) return;
    try {
      const res = await fetch(`/api/reports/${filename}`, { method: "DELETE" });
      if (res.ok) {
        queryClient.invalidateQueries({ queryKey: ["reports"] });
      }
    } catch (error) {
      console.error("Delete failed", error);
    }
  };

  if (isLoading)
    return (
      <div className="p-8 text-center text-[10px] font-black uppercase animate-pulse">
        Cargando Archivos...
      </div>
    );

  const safeReports = Array.isArray(reports) ? reports : [];

  return (
    <ScrollArea className="h-[600px]">
      <div className="space-y-3 py-4 px-3">
        {safeReports.map((report) => (
          <div
            key={report.name}
            className="bg-white/5 p-3 rounded-xl border border-white/5 flex items-center gap-3 group hover:bg-white/10 transition-all duration-300"
          >
            <div className="bg-primary/20 p-2 rounded-lg shrink-0 group-hover:bg-primary group-hover:text-black transition-colors">
              <FileText
                size={14}
                className="text-primary group-hover:text-black"
              />
            </div>

            <div className="min-w-0 flex-1 overflow-hidden">
              <p
                className="text-[10px] font-black uppercase tracking-tight truncate block"
                title={report.name}
              >
                {report.name}
              </p>
              <p className="text-[8px] text-muted-foreground uppercase font-bold tracking-widest truncate">
                {report.size} • {report.date}
              </p>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDownload(report.name)}
                className="h-8 w-8 rounded-lg hover:bg-primary/20 hover:text-primary transition-colors"
                title="Descargar"
              >
                <Download size={14} />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(report.name)}
                className="h-8 w-8 rounded-lg hover:bg-destructive/20 hover:text-destructive transition-colors opacity-0 group-hover:opacity-100"
                title="Eliminar"
              >
                <Trash2 size={14} />
              </Button>
            </div>
          </div>
        ))}
        {safeReports.length === 0 && (
          <div className="text-center py-10 opacity-20 text-[10px] font-black uppercase">
            Sin registros
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
