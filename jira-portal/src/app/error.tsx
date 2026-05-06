"use client"

import { AlertTriangle, RefreshCcw } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 text-center">
      <div className="bg-destructive/10 p-6 rounded-2xl border border-destructive/20 mb-8 shadow-[0_0_40px_rgba(255,59,59,0.1)]">
        <AlertTriangle className="text-destructive w-16 h-16" />
      </div>
      <h1 className="text-3xl font-black text-foreground uppercase tracking-tighter mb-4 italic">
        FALLO CRÍTICO <span className="text-destructive not-italic">DE SISTEMA</span>
      </h1>
      <p className="max-w-md text-muted-foreground uppercase text-[10px] font-bold tracking-widest mb-8 leading-relaxed">
        Se ha detectado una interrupción en el flujo de telemetría.
        Industrial Protocol: ERROR_CODE_{error.digest || '500_STALE'}.
      </p>
      <Button 
        onClick={() => reset()}
        className="h-14 px-8 bg-destructive text-white hover:bg-destructive/80 font-black tracking-widest uppercase rounded-xl transition-all active:scale-95 flex gap-3"
      >
        <RefreshCcw className="w-5 h-5" />
        REINICIAR NODO
      </Button>
    </div>
  )
}
