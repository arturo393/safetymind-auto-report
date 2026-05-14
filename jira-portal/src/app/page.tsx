"use client"

import { useState, Suspense, lazy } from "react"
import { 
  FileText, 
  History, 
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Toggle } from "@/components/ui/toggle"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

// SafetyMind Atomic Components
import { Header } from "@/components/organisms/Header"
import { ProjectSelector } from "@/components/molecules/ProjectSelector"
import { StatsGrid } from "@/components/organisms/StatsGrid"
import { useProjects, useOllamaStatus } from "@/hooks/useProjects"
import { useQueryClient } from "@tanstack/react-query"

// PERFORMANCE: Lazy Loading for heavy history section
const HistoryScroll = lazy(() => import("@/components/organisms/HistoryScroll").then(m => ({ default: m.HistoryScroll })))

export default function PMODashboard() {
  const [activeProject, setActiveProject] = useState<string>("")
  const [reportType, setReportType] = useState("progress")
  const [isGenerating, setIsGenerating] = useState(false)
  const [opStatus, setOpStatus] = useState<string | null>(null)
  const [useAI, setUseAI] = useState(true)
  const [aiModel, setAiModel] = useState("llama3")

  const { projects, loading } = useProjects()
  const ollamaStatus = useOllamaStatus()
  const queryClient = useQueryClient()

  const handleGenerate = async () => {
    if (!activeProject) return
    setIsGenerating(true)
    setOpStatus("PROCESANDO...")
    
        try {
          const res = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              project_key: activeProject,
              report_type: reportType,
              use_ai: useAI,
              ai_model: aiModel
            })
          })
      if (!res.ok) throw new Error("Generation failure")
      
      const data = await res.json()
      const engine = data.engine || "html"
      setOpStatus(`ÉXITO: ${data.filename} [${engine.toUpperCase()}]`)
      
      // Force UI sync to show the new file in History Log
      queryClient.invalidateQueries({ queryKey: ["reports"] })

    } catch (error) {
      setOpStatus("FALLO DE GENERACIÓN")
    } finally {
      setIsGenerating(false)
      setTimeout(() => setOpStatus(null), 5000)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/30 antialiased">
      <Header />

      <main className="flex-1 p-6 max-w-[1400px] mx-auto w-full grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        <div className="lg:col-span-1 space-y-6">
          <ProjectSelector 
            projects={projects}
            activeProject={activeProject}
            setActiveProject={setActiveProject}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />

          <Card className="bg-card border-white/5 shadow-xl ring-1 ring-white/5">
            <CardHeader className="bg-white/5 border-b border-white/5">
              <CardTitle className="text-xs uppercase tracking-[0.3em] text-primary font-black">⚙️ CONFIGURACIÓN</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              <div className="space-y-4">
                <Label className="text-[10px] uppercase font-black text-muted-foreground tracking-widest">Tipo de Entregable</Label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    { id: "kickoff", label: "Kickoff Meeting" },
                    { id: "progress", label: "Monthly Progress" },
                    { id: "final", label: "Final Delivery" }
                  ].map((type) => (
                    <Button
                      key={type.id}
                      variant={reportType === type.id ? "default" : "outline"}
                      onClick={() => setReportType(type.id)}
                      className={`justify-start h-12 rounded-lg border-white/5 font-black uppercase text-[10px] tracking-widest transition-all ${
                        reportType === type.id ? "bg-primary text-black" : "bg-white/5 text-muted-foreground hover:text-white"
                      }`}
                    >
                      {type.label}
                    </Button>
                  ))}
                </div>
              </div>

<Separator className="bg-white/5" />

              <div className="space-y-3">
                <Label className="text-[10px] uppercase font-black text-muted-foreground tracking-widest">AI Model</Label>
                <Select value={aiModel} onValueChange={(v) => setAiModel(v || "llama3")}>
                  <SelectTrigger className="h-10 bg-white/5 border-white/10 rounded-lg">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-white/10">
                    <SelectItem value="llama3" className="focus:bg-primary focus:text-black">Llama 3</SelectItem>
                    <SelectItem value="llama3.2" className="focus:bg-primary focus:text-black">Llama 3.2</SelectItem>
                    <SelectItem value="mistral" className="focus:bg-primary focus:text-black">Mistral</SelectItem>
                    <SelectItem value="phi" className="focus:bg-primary focus:text-black">Phi</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator className="bg-white/5" />

              <div className="pt-2">
                {isGenerating && (
                  <div className="mb-3 space-y-2">
                    <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                      <span>Procesando...</span>
                      <span className="text-primary">Jira Data</span>
                    </div>
                    <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-primary animate-pulse w-2/3 transition-all duration-500" />
                    </div>
                  </div>
                )}

                {opStatus && (
                  <div className={`text-center text-[10px] font-black uppercase tracking-widest p-3 rounded-lg border ${opStatus.includes('ÉXITO') ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-primary/10 text-primary border-primary/20'}`}>
                    {opStatus}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="bg-white/5 border border-white/10 p-1.5 rounded-xl w-full grid grid-cols-3 h-14 ring-1 ring-white/5">
              <TabsTrigger value="overview" className="rounded-[10px] data-[state=active]:bg-primary data-[state=active]:text-black font-black uppercase text-[10px] tracking-widest transition-all">VISTA GENERAL</TabsTrigger>
              <TabsTrigger value="config" className="rounded-[10px] data-[state=active]:bg-primary data-[state=active]:text-black font-black uppercase text-[10px] tracking-widest transition-all">PARAMETROS</TabsTrigger>
              <TabsTrigger value="insights" className="rounded-[10px] data-[state=active]:bg-primary data-[state=active]:text-black font-black uppercase text-[10px] tracking-widest transition-all">IA INSIGHTS</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-6 mt-6 focus-visible:outline-none">
              <StatsGrid loading={loading} />

              <Card className="bg-card border-white/5 shadow-2xl min-h-[440px] ring-1 ring-white/10 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
                <CardHeader>
                  <CardTitle className="text-primary uppercase tracking-tighter font-black text-xl">Reporte Estratégico Detallado</CardTitle>
                  <CardDescription className="text-[10px] uppercase font-bold text-muted-foreground tracking-[0.2em]">Sincronizado vía Core de Telemetría Industrial</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center py-24 text-muted-foreground">
                  <div className="relative mb-6">
                    <FileText size={80} strokeWidth={1} className="opacity-5 group-hover:opacity-10 transition-opacity" />
                    <div className="absolute inset-0 bg-primary/5 blur-3xl rounded-full" />
                  </div>
                  <p className="text-[10px] uppercase tracking-[0.4em] font-black opacity-40">
                    {activeProject ? `Nodo ${activeProject} Seleccionado - Listo para Generar` : "Seleccione un nodo para iniciar diagnóstico"}
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="config" className="space-y-6 mt-6">
              <Card className="bg-card border-white/5 p-6">
                <h3 className="text-primary font-black uppercase text-xs mb-4">Configuración Técnica de Nodo</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 p-4 rounded-lg border border-white/5">
                      <p className="text-[9px] text-muted-foreground uppercase font-black">Project Key</p>
                      <p className="text-sm font-bold text-white">{activeProject || "---"}</p>
                    </div>
                    <div className="bg-white/5 p-4 rounded-lg border border-white/5">
                      <p className="text-[9px] text-muted-foreground uppercase font-black">Sync Frequency</p>
                      <p className="text-sm font-bold text-white">Real-Time (Webhook)</p>
                    </div>
                  </div>
                  <div className="bg-white/5 p-4 rounded-lg border border-white/5">
                    <p className="text-[9px] text-muted-foreground uppercase font-black">Operational Buffer</p>
                    <div className="w-full bg-white/5 h-2 rounded-full mt-2 overflow-hidden">
                      <div className="bg-primary w-3/4 h-full" />
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-6 mt-6">
              <Card className="bg-primary/5 border border-primary/20 p-6 relative overflow-hidden">
                <h3 className="text-primary font-black uppercase text-xs mb-4">Análisis de Misión Crítica</h3>
                {activeProject ? (
                  <>
                    <p className="text-sm text-gray-300 leading-relaxed max-w-[90%]">
                      Sincronizando telemetría para <span className="text-primary font-bold">{activeProject}</span>. El motor de análisis está procesando el backlog de Jira para detectar riesgos en el cronograma.
                    </p>
                    <div className="mt-6 flex gap-3">
                      <Badge className="bg-primary text-black">JIRA LIVE</Badge>
                      <Badge className={ollamaStatus === "ready" ? "bg-green-600 text-white" : "bg-yellow-600 text-black"}>
                        {ollamaStatus === "ready" ? "OLLAMA READY" : "OLLAMA OFFLINE"}
                      </Badge>
                    </div>
                  </>
                ) : (
                  <p className="text-xs text-muted-foreground uppercase font-black tracking-widest">Seleccione un proyecto de Jira Cloud para activar el análisis.</p>
                )}
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <Card className="bg-card text-foreground border-white/5 shadow-2xl h-full flex flex-col ring-1 ring-white/5 overflow-hidden">
            <CardHeader className="bg-white/5 border-b border-white/5">
              <div className="flex items-center gap-2 text-primary">
                <History size={18} />
                <CardTitle className="text-[10px] tracking-[0.4em] uppercase font-black">History Log</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Suspense fallback={<div className="p-8 text-[10px] uppercase font-black text-muted-foreground animate-pulse">Cargando Historial...</div>}>
                <HistoryScroll />
              </Suspense>
            </CardContent>
          </Card>
        </div>
      </main>

      <footer className="p-6 border-t border-white/10 bg-card/80 backdrop-blur-xl flex flex-col md:flex-row justify-between items-center px-8 mt-auto gap-4">
        <p className="text-[10px] uppercase font-black tracking-widest text-muted-foreground opacity-30">© 2026 SafetyMind Elite Core • Mission Critical Only</p>
        <div className="flex items-center gap-6 text-[10px] font-black text-muted-foreground">
          <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(255,237,1,0.5)]"></div> API SECURE</span>
          <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div> JIRA CLOUD SYNC</span>
          <Badge className="bg-white/5 text-white/40 border-none font-black text-[9px] uppercase px-3 py-1">V4.1-ELITE</Badge>
        </div>
      </footer>
    </div>
  )
}
