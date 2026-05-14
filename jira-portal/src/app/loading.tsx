import { Shield } from "lucide-react"

export default function Loading() {
  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 text-center">
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full animate-pulse" />
        <div className="relative bg-card p-6 rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(255,237,1,0.1)]">
          <Shield className="text-primary w-12 h-12 animate-pulse" />
        </div>
      </div>
      <h2 className="text-xl font-black tracking-widest text-foreground uppercase italic mb-2">
        Sincronizando Core <span className="text-primary not-italic">SafetyMind</span>
      </h2>
      <div className="flex gap-1 justify-center">
        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]" />
        <div className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" />
      </div>
    </div>
  )
}
