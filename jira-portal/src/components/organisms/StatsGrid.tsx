import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { HelpCircle } from "lucide-react"

interface StatsGridProps {
  loading: boolean
}

export function StatsGrid({ loading }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* HEALTH SCORE: INDUSTRIAL GAUGE STYLE */}
      <Card className="bg-card border-white/5 shadow-lg ring-1 ring-white/5 group hover:ring-primary/20 transition-all duration-500">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardDescription className="text-[10px] font-black tracking-[0.3em] text-primary uppercase">System Health</CardDescription>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle size={12} className="text-primary/40 hover:text-primary transition-colors" />
                </TooltipTrigger>
                <TooltipContent side="top">
                  Disponibilidad del Nodo Maestro y latencia de API Jira Cloud
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <CardTitle className="text-4xl font-black text-foreground font-mono tracking-tighter">
            87<span className="text-primary/50 text-2xl">%</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
            <div 
              className="h-full bg-primary w-[87%] shadow-[0_0_20px_rgba(255,237,1,0.4)] transition-all duration-1000 ease-out group-hover:bg-white"
            />
          </div>
          <div className="mt-4 space-y-1">
            <p className="text-[9px] text-muted-foreground uppercase font-black tracking-widest">Estado Operativo</p>
            <p className="text-[8px] text-white/40 leading-relaxed uppercase font-bold">
              Disponibilidad del Nodo Maestro y latencia de respuesta de la API Jira. Valores de 80%+ indican operación nominal.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* JIRA SYNC: REAL-TIME TELEMETRY INDICATOR */}
      <Card className="bg-card border-white/5 shadow-lg ring-1 ring-white/5 group hover:ring-primary/20 transition-all">
        <CardHeader className="pb-2">
          <CardDescription className="text-[10px] font-black tracking-[0.3em] text-primary uppercase">Data Ingestion</CardDescription>
          <CardTitle className="text-4xl font-black text-foreground font-mono tracking-tighter">
            {loading ? "---" : "LIVE"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Badge className="bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 font-black px-4 py-1.5 uppercase text-[10px] tracking-widest shadow-inner mb-4">
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
                SYNCING...
              </span>
            ) : (
              "ENLACE ESTABLE"
            )}
          </Badge>
          <div className="space-y-1">
            <p className="text-[9px] text-muted-foreground uppercase font-black tracking-widest">Flujo de Telemetría</p>
            <p className="text-[8px] text-white/40 leading-relaxed uppercase font-bold">
              Sincronización en tiempo real con Jira Cloud. Cache activo para optimización de ancho de banda local.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* PENDING TASKS: SEVERITY MATRIX INDICATOR */}
      <Card className="bg-card border-white/5 shadow-lg ring-1 ring-white/5 group hover:ring-primary/20 transition-all">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardDescription className="text-[10px] font-black tracking-[0.3em] text-primary uppercase">Security Backlog</CardDescription>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle size={12} className="text-primary/40 hover:text-primary transition-colors" />
                </TooltipTrigger>
                <TooltipContent side="top">
                  Distribución de incidentes P1/P2/P3 sin resolver en el proyecto
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <CardTitle className="text-4xl font-black text-foreground font-mono tracking-tighter">12</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="flex-1 h-3 rounded-md bg-destructive shadow-[0_0_15px_rgba(255,59,59,0.2)]" title="P1: Critical" />
            <div className="flex-1 h-3 rounded-md bg-primary/40" title="P2: Warning" />
            <div className="flex-1 h-3 rounded-md bg-white/10" title="P3: Minor" />
          </div>
          <div className="mt-4 space-y-1">
            <p className="text-[9px] text-muted-foreground uppercase font-black tracking-widest">Matriz de Severidad</p>
            <p className="text-[8px] text-white/40 leading-relaxed uppercase font-bold">
              Distribución de incidentes P1/P2/P3. El backlog crítico impacta directamente el cronograma del reporte.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
