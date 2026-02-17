import React from "react";
import { ShieldCheck, Github } from "lucide-react";

function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30">
      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/20 rounded-full blur-[120px] mix-blend-screen animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500/20 rounded-full blur-[120px] mix-blend-screen animate-pulse-slow delay-1000" />
      </div>

      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-50 border-b border-white/5 bg-slate-950/60 backdrop-blur-xl">
          <div className="container mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <ShieldCheck className="w-6 h-6 text-blue-400" />
              </div>
              <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-blue-100 to-indigo-200 bg-clip-text text-transparent">
                API Guardian
              </span>
            </div>
            
            <nav className="flex items-center gap-6">
              <a 
                href="#" 
                className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                Documentation
              </a>
              <a 
                href="https://github.com/das-kushal/API-Guradian" 
                target="_blank" 
                rel="noreferrer"
                className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-full transition-all"
              >
                <Github className="w-5 h-5" />
              </a>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 container mx-auto px-6 py-12">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-white/5 py-8 mt-auto">
          <div className="container mx-auto px-6 text-center text-slate-500 text-sm">
            <p>&copy; {new Date().getFullYear()} API Guardian. Secure your endpoints.</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default Layout;
