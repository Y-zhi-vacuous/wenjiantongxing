import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { PenLine, FileText, TrendingUp, ArrowRight, Sparkles, Target } from 'lucide-react'
import api from '../../api/client'
import type { Essay } from '../../types'

const cardClass = "bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] transition-all duration-300"

export default function Dashboard() {
  const [essays, setEssays] = useState<Essay[]>([])
  const [ability, setAbility] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/essays?limit=5'),
      api.get('/ability/me'),
    ]).then(([essayRes, abilityRes]) => {
      setEssays(essayRes.data.essays || essayRes.data)
      setAbility(abilityRes.data)
    }).finally(() => setLoading(false))
  }, [])

  const gradedCount = essays.filter((e) => e.status === 'graded').length
  const hasAbility = ability && ability.essay_count > 0

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">我的首页</h2>
          <p className="text-apple-secondary mt-1">你的写作成长之路</p>
        </div>
        <Link
          to="/student/write"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.97] transition-all duration-200 shadow-lg shadow-blue-500/20"
        >
          <PenLine className="w-4 h-4" />
          写作文
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { icon: FileText, label: '作文总数', value: essays.length, color: 'text-apple-accent', bg: 'bg-blue-50' },
          { icon: TrendingUp, label: '已批改', value: gradedCount, color: 'text-apple-green', bg: 'bg-green-50' },
          { icon: Target, label: '能力均分', value: hasAbility ? ability.overall_score : '-', color: 'text-apple-orange', bg: 'bg-orange-50' },
          { icon: Sparkles, label: '薄弱项', value: hasAbility ? ability.weaknesses?.length || 0 : '-', color: 'text-purple-500', bg: 'bg-purple-50' },
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

      {/* Ability Snapshot */}
      {hasAbility && (
        <Link to="/student/ability" className={`${cardClass} p-6 block hover:-translate-y-0.5`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-apple-accent" />
              <h3 className="font-semibold text-apple-text">能力总览</h3>
            </div>
            <ArrowRight className="w-4 h-4 text-apple-disabled" />
          </div>
          <div className="grid grid-cols-4 gap-6">
            {[
              { label: '立意', score: ability.abilities?.thesis, color: '#FF3B30' },
              { label: '内容', score: ability.abilities?.content, color: '#007AFF' },
              { label: '语言', score: ability.abilities?.language, color: '#34C759' },
              { label: '结构', score: ability.abilities?.structure, color: '#FF9500' },
              { label: '文面', score: ability.abilities?.penmanship, color: '#AF52DE' },
            ].map(({ label, score, color }) => (
              <div key={label} className="text-center">
                <div className="text-2xl font-bold text-apple-text">{score}</div>
                <div className="text-xs text-apple-secondary mt-1">{label}</div>
                <div className="mt-2 h-1.5 bg-apple-bg rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${score}%`, background: color }} />
                </div>
              </div>
            ))}
          </div>
        </Link>
      )}

      {/* Recent Essays */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-apple-text">最近作文</h3>
          <Link to="/student/history" className="text-sm text-apple-accent flex items-center gap-1 hover:underline">
            查看全部 <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        {loading ? (
          <div className="text-center py-12 text-apple-secondary">加载中...</div>
        ) : essays.length === 0 ? (
          <div className={`${cardClass} p-16 text-center`}>
            <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <PenLine className="w-8 h-8 text-apple-accent" />
            </div>
            <p className="text-apple-text font-medium mb-1">开始你的第一篇作文</p>
            <p className="text-sm text-apple-secondary mb-6">AI 将为你提供专业的批改和提升建议</p>
            <Link
              to="/student/write"
              className="inline-flex items-center gap-2 px-6 py-3 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.97] transition-all duration-200 shadow-lg shadow-blue-500/20"
            >
              <PenLine className="w-4 h-4" />
              写一篇作文
            </Link>
          </div>
        ) : (
          <div className="space-y-2.5">
            {essays.map((essay) => {
              const s = essay.status === 'graded' ? { text: '已批改', cls: 'bg-green-50 text-green-600' } :
                       essay.status === 'grading' ? { text: '批改中', cls: 'bg-orange-50 text-orange-600' } :
                       { text: '待批改', cls: 'bg-gray-100 text-apple-secondary' }
              return (
                <Link
                  key={essay.id}
                  to={`/student/essay/${essay.id}`}
                  className={`${cardClass} p-4 flex items-center justify-between hover:-translate-y-0.5`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-apple-bg rounded-xl flex items-center justify-center">
                      <FileText className="w-5 h-5 text-apple-disabled" />
                    </div>
                    <div>
                      <h4 className="font-medium text-apple-text text-sm">{essay.title || '未命名作文'}</h4>
                      <p className="text-xs text-apple-secondary mt-0.5">
                        {essay.word_count} 字 · {new Date(essay.submitted_at).toLocaleDateString('zh-CN')}
                      </p>
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-3 py-1 rounded-full ${s.cls}`}>{s.text}</span>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
