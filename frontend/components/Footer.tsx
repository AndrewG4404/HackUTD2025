export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-purple-500/30 bg-black/50 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold text-gradient mb-2">✨ VendorLens</h3>
            <p className="text-amber-200/70 text-sm">
              Mystical AI sorcery for vendor divination
            </p>
            <div className="mt-4">
              <p className="text-xs text-purple-400">✨ Enchanted by NVIDIA Nemotron</p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-amber-300 mb-3 uppercase tracking-wide">Mystical Realms</h4>
            <ul className="space-y-2">
              <li>
                <a href="/apply" className="text-gray-400 hover:text-purple-300 transition-colors text-sm">
                  ✨ Vendor Portal
                </a>
              </li>
              <li>
                <a href="/assess" className="text-gray-400 hover:text-purple-300 transition-colors text-sm">
                  🔮 Oracle Chamber
                </a>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-sm font-semibold text-amber-300 mb-3 uppercase tracking-wide">Sacred Quest</h4>
            <p className="text-gray-400 text-sm mb-3">
              Goldman Sachs • The Vendor Codex
            </p>
            <p className="text-xs text-purple-400">
              🏆 HackUTD 2025
            </p>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-purple-500/30 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm">
            © 2025 VendorLens. Forged in the fires of HackUTD.
          </p>
          <div className="flex items-center gap-2 mt-4 md:mt-0">
            <span className="text-xs text-purple-400">🔮 7 Mystical Sages</span>
            <span className="text-purple-600">•</span>
            <span className="text-xs text-purple-400">⏳ 5 Minutes of Magic</span>
            <span className="text-purple-600">•</span>
            <span className="text-xs text-purple-400">✨ Crystal Clear</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

