import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, BookOpen, FileText, TrendingUp, Target, ArrowRight } from 'lucide-react'
import api from '../../api/client'

const cardClass = "bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] transition-all duration-300"

export default function TeacherDashboard() {
  const [classes, setClasses] = useState<any[]>([])
  const [recentEssays, setRecentEssays] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/classes'),
      api.get('/essays?limit=10'),
    ]).then(([cRes, eRes]) => {
      setClasses(cRes.data.classes || cRes.data)
      setRecentEssays(eRes.data.essays || eRes.data)
    }).finally(() => setLoading(false))
  }, [])

  const graded = recentEssays.filter((e: any) => e.status === 'graded').length

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">教师工作台</h2>
          <p className="text-apple-secondary mt-1">管理班级与作文教学</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { icon: Users, label: '班级数', value: classes.length, color: 'text-apple-accent', bg: 'bg-blue-50' },
          { icon: FileText, label: '作文提交', value: recentEssays.length, color: 'text-apple-green', bg: 'bg-green-50' },
          { icon: TrendingUp, label: '已批改', value: graded, color: 'text-apple-orange', bg: 'bg-orange-50' },
          { icon: Target, label: '待批改', value: recentEssays.length - graded, color: 'text-purple-500', bg: 'bg-purple-50' },
        ].map(({ icon: Icon, label, value, color, bg }) => (
          <div key={label} className={`${cardClass} p-5 text-center`}>
            <div className={`w-10 h-10 ${bg} rounded-xl flex items-center justify-center mx-auto mb-3`}>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <div className="text-2xl font-bold text-apple-text">{loading ? '-' : value}</div>
            <div className="text-xs text-apple-secondary mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 gap-4">
        <Link to="/teacher/classes" className={`${cardClass} p-6 block hover:-translate-y-0.5 group`}>
          <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
            <Users className="w-6 h-6 text-apple-accent" />
          </div>
          <h3 className="font-semibold text-apple-text mb-1">班级管理</h3>
          <p className="text-sm text-apple-secondary">管理班级，查看学生列表和能力画像</p>
          <div className="flex items-center gap-1 text-sm text-apple-accent mt-3 font-medium">
            进入 <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
        <Link to="/teacher/topics" className={`${cardClass} p-6 block hover:-translate-y-0.5 group`}>
          <div className="w-12 h-12 bg-green-50 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
            <BookOpen className="w-6 h-6 text-apple-green" />
          </div>
          <h3 className="font-semibold text-apple-text mb-1">题库管理</h3>
          <p className="text-sm text-apple-secondary">管理作文题目，添加自定义题目</p>
          <div className="flex items-center gap-1 text-sm text-apple-accent mt-3 font-medium">
            进入 <ArrowRight className="w-3.5 h-3.5" />
          </div>
        </Link>
      </div>

      {/* Recent Essays */}
      <div>
        <h3 className="text-lg font-semibold text-apple-text mb-4">最近提交的作文</h3>
        {loading ? (
          <div className="text-center py-12 text-apple-secondary">加载中...</div>
        ) : recentEssays.length === 0 ? (
          <div className={`${cardClass} p-16 text-center`}>
            <FileText className="w-10 h-10 mx-auto mb-3 text-apple-disabled" />
            <p className="text-apple-secondary">暂无作文提交</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {recentEssays.map((e: any) => (
              <Link key={e.id} to={`/teacher/essay/${e.id}`}
                    className={`${cardClass} p-4 flex items-center justify-between hover:-translate-y-0.5`}>
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-apple-disabled" />
                  <div>
                    <span className="font-medium text-apple-text text-sm">{e.title || '未命名'}</span>
                    <span className="text-xs text-apple-secondary ml-2">{e.word_count} 字</span>
                  </div>
                </div>
                <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                  e.status === 'graded' ? 'bg-green-50 text-green-600' :
                  e.status === 'grading' ? 'bg-orange-50 text-orange-600' :
                  'bg-gray-100 text-apple-secondary'
                }`}>
                  {e.status === 'graded' ? '已批改' : e.status === 'grading' ? '批改中' : '待批改'}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
