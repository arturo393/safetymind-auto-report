import { Play, CloudLightning } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface ProjectSelectorProps {
  projects: Record<string, string>
  activeProject: string
  setActiveProject: (id: string) => void
  onGenerate: () => void
  isGenerating: boolean
}

export function ProjectSelector({ 
  projects, 
  activeProject, 
  setActiveProject, 
  onGenerate, 
  isGenerating 
}: ProjectSelectorProps) {
  return (
    <Card className="bg-card border-white/5 shadow-2xl ring-1 ring-white/5">
      <CardHeader className="bg-white/5 border-b border-white/5">
        <CardTitle className="text-xs uppercase tracking-[0.3em] text-primary font-black">PROYECTO ACTIVO</CardTitle>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="project" className="text-[10px] uppercase font-bold tracking-widest opacity-70">
              Seleccionar de Jira Cloud
            </Label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <CloudLightning size={12} className="text-primary/40 hover:text-primary transition-colors" />
                </TooltipTrigger>
                <TooltipContent side="right">
                  Listado sincronizado de instancias activas en la organización
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <Select onValueChange={(v) => setActiveProject(v || "")} value={activeProject}>
            <SelectTrigger id="project" className="h-12 bg-white/5 border-white/10 rounded-xl focus:ring-primary shadow-inner">
              <SelectValue placeholder="Seleccione un proyecto..." />
            </SelectTrigger>
            <SelectContent className="bg-card border-white/10 text-foreground">
              {Object.entries(projects).map(([key, name]) => (
                <SelectItem key={key} value={key} className="focus:bg-primary focus:text-black">
                  {key} - {name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Button 
          onClick={onGenerate} 
          aria-label={isGenerating ? "Generando reporte estratégico" : "Iniciar generación de reporte industrial"}
          className={`w-full h-12 font-black text-sm tracking-widest uppercase transition-all duration-300 rounded-xl ${
            isGenerating ? 'bg-muted opacity-50' : 'bg-primary hover:bg-primary/80 text-black hover:scale-[1.02] active:scale-95 shadow-[0_0_20px_rgba(255,237,1,0.1)]'
          }`}
          disabled={!activeProject || isGenerating}
        >
          {isGenerating ? (
            <CloudLightning className="mr-2 animate-pulse" />
          ) : (
            <Play className="mr-2 fill-current size-4" />
          )}
          {isGenerating ? "GENERANDO..." : "INICIAR REPORTE"}
        </Button>
      </CardContent>
    </Card>
  )
}
