import { Link, useLocation } from 'react-router-dom'
import { PenLine, History, Settings, GraduationCap, LayoutDashboard, Target } from 'lucide-react'

const navItems = [
  { to: '/student/dashboard', icon: LayoutDashboard, label: '首页' },
  { to: '/student/write', icon: PenLine, label: '写作文' },
  { to: '/student/ability', icon: Target, label: '能力' },
  { to: '/student/history', icon: History, label: '历史' },
  { to: '/student/settings', icon: Settings, label: '设置' },
]

export default function StudentNav() {
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-2xl bg-white/70 border-b border-black/5">
      <div className="max-w-4xl mx-auto px-5 h-12 flex items-center justify-between">
        <Link to="/student/dashboard" className="flex items-center gap-2 text-apple-text hover:opacity-80 transition-opacity">
          <div className="w-7 h-7 bg-apple-accent rounded-lg flex items-center justify-center">
            <GraduationCap className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-sm tracking-tight">文鉴同行</span>
        </Link>
        <div className="flex items-center gap-0.5">
          {navItems.map(({ to, icon: Icon, label }) => {
            const active = location.pathname.startsWith(to)
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  active
                    ? 'bg-apple-accent/10 text-apple-accent'
                    : 'text-apple-secondary hover:text-apple-text hover:bg-black/[0.04]'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
