export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-white/10 bg-black/50 backdrop-blur-xl">
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-xl font-bold text-white mb-2">VendorLens</h3>
            <p className="text-gray-400 text-sm">
              AI-powered vendor onboarding for enterprise
            </p>
            <div className="mt-4">
              <p className="text-xs text-gray-500">Powered by NVIDIA Nemotron</p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wide">Platform</h4>
            <ul className="space-y-2">
              <li>
                <a href="/apply" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Vendor Portal
                </a>
              </li>
              <li>
                <a href="/assess" className="text-gray-400 hover:text-white transition-colors text-sm">
                  Internal Dashboard
                </a>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wide">Built For</h4>
            <p className="text-gray-400 text-sm mb-3">
              Goldman Sachs Enterprise Vendor Onboarding
            </p>
            <p className="text-xs text-gray-500">
              HackUTD 2025
            </p>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm">
            © 2025 VendorLens. Built for HackUTD.
          </p>
          <div className="flex items-center gap-2 mt-4 md:mt-0">
            <span className="text-xs text-gray-500">7 AI Agents</span>
            <span className="text-gray-600">•</span>
            <span className="text-xs text-gray-500">5 Minute Evaluations</span>
            <span className="text-gray-600">•</span>
            <span className="text-xs text-gray-500">100% Transparent</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

