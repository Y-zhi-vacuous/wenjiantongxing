import { Link, useLocation } from 'react-router-dom'
import { GraduationCap, LayoutDashboard, Users, BookOpen, Settings, FileText } from 'lucide-react'

const navItems = [
  { to: '/teacher/dashboard', icon: LayoutDashboard, label: '概览' },
  { to: '/teacher/grading', icon: FileText, label: '批改' },
  { to: '/teacher/classes', icon: Users, label: '班级' },
  { to: '/teacher/topics', icon: BookOpen, label: '题库' },
  { to: '/teacher/settings', icon: Settings, label: '设置' },
]

export default function TeacherNav() {
  const location = useLocation()

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-2xl bg-white/70 border-b border-black/5">
      <div className="max-w-5xl mx-auto px-5 h-12 flex items-center justify-between">
        <Link to="/teacher/dashboard" className="flex items-center gap-2 text-apple-text hover:opacity-80 transition-opacity">
          <div className="w-7 h-7 bg-apple-accent rounded-lg flex items-center justify-center">
            <GraduationCap className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-sm tracking-tight">文鉴同行 · 教师</span>
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
