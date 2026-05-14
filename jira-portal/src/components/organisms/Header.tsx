import { Shield } from "lucide-react"
import { Z_INDEX } from "@/constants/z-index"

export function Header() {
  return (
    <header 
      className="bg-card/50 backdrop-blur-md border-b border-white/10 p-4 flex justify-between items-center sticky top-0"
      style={{ zIndex: Z_INDEX.STICKY_NAV }}
    >
      <div className="flex items-center gap-3">
        <div className="bg-primary p-2.5 rounded-xl shadow-[0_0_15px_rgba(255,237,1,0.2)]">
          <Shield className="text-black w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl font-black tracking-tighter uppercase italic">
            SAFETYMIND <span className="text-primary font-normal not-italic">PMO</span>
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground font-bold">
            Industrial Strategic Core v4.1
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right hidden md:block">
          <p className="text-[10px] uppercase text-muted-foreground font-bold">Operational Lead</p>
          <p className="text-sm font-black tracking-tight">AUTHORIZED USER</p>
        </div>
        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-black font-black shadow-inner">
          <Shield className="w-5 h-5" />
        </div>
      </div>
    </header>
  )
}
