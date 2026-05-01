import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Target, TrendingUp, Sparkles, AlertCircle } from 'lucide-react'
import api from '../../api/client'

interface AbilityData {
  student_id: number
  display_name: string
  overall_score: number
  essay_count: number
  abilities: { content: number; language: number; structure: number; penmanship: number }
  score_history: { essay_id: number; date: string; title: string; total_score: number; content: number; language: number; structure: number; penmanship: number }[]
  strengths: string[]
  weaknesses: string[]
  improvement_plan: { dimension: string; level: string; score: number; suggestions: string[] }[]
  message?: string
}

export default function TeacherStudentAbility() {
  const { studentId } = useParams<{ studentId: string }>()
  const [data, setData] = useState<AbilityData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!studentId) return
    api.get(`/ability/student/${studentId}`).then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [studentId])

  if (loading) return <div className="text-center py-24 text-apple-secondary">加载中...</div>

  if (!data || data.essay_count === 0) {
    return (
      <div className="space-y-6">
        <Link to="/teacher/classes" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text">
          <ArrowLeft className="w-4 h-4" /><span className="text-sm">返回</span>
        </Link>
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-12 text-center">
          <Sparkles className="w-12 h-12 mx-auto mb-4 text-apple-disabled" />
          <p className="text-apple-text font-medium">{data?.display_name || '学生'} 还没有作文批改记录</p>
          <p className="text-sm text-apple-secondary mt-1">提交并获得批改后将自动生成能力画像</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-12">
      <Link to="/teacher/classes" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text">
        <ArrowLeft className="w-4 h-4" /><span className="text-sm">返回班级</span>
      </Link>

      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">{data.display_name} 的能力画像</h2>
        <p className="text-apple-secondary mt-1">共 {data.essay_count} 篇作文</p>
      </div>

      {/* Overall Score */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-8 text-center">
        <div className="text-xs font-semibold text-apple-secondary tracking-wide uppercase mb-2">综合均分</div>
        <div className="text-7xl font-bold text-apple-text tracking-tighter">{data.overall_score}</div>
        <div className="text-sm text-apple-secondary mt-1">满分 45</div>
        <div className="flex justify-center gap-8 mt-6 pt-6 border-t border-apple-divider">
          {[
            { label: '内容', score: data.abilities.content, color: '#007AFF' },
            { label: '语言', score: data.abilities.language, color: '#34C759' },
            { label: '结构', score: data.abilities.structure, color: '#FF9500' },
            { label: '卷面', score: data.abilities.penmanship, color: '#AF52DE' },
          ].map(({ label, score, color }) => (
            <div key={label} className="text-center flex-1">
              <div className="text-2xl font-bold" style={{ color }}>{score}</div>
              <div className="text-xs text-apple-secondary mt-1">{label}</div>
              <div className="mt-2 h-1.5 bg-[#F2F2F7] rounded-full overflow-hidden">
                <div className="h-full rounded-full" style={{ width: `${score}%`, background: color }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-5 h-5 text-apple-green" />
            <h3 className="font-semibold text-apple-text">优势领域</h3>
          </div>
          {data.strengths?.map((s) => (
            <div key={s} className="bg-green-50 rounded-xl px-4 py-2.5 text-sm text-green-700 mb-2">{s}</div>
          ))}
        </div>
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5 text-apple-orange" />
            <h3 className="font-semibold text-apple-text">待提升领域</h3>
          </div>
          {data.weaknesses?.map((w) => (
            <div key={w} className="bg-orange-50 rounded-xl px-4 py-2.5 text-sm text-orange-700 mb-2">{w}</div>
          ))}
        </div>
      </div>

      {/* Score History */}
      {data.score_history && data.score_history.length > 0 && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">分数趋势</h3>
          </div>
          <div className="flex items-end gap-3 h-32">
            {data.score_history.map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-xs font-semibold text-apple-text">{h.total_score}</span>
                <div className="w-full bg-apple-accent rounded-t-lg" style={{ height: `${(h.total_score / 50) * 100}%`, minHeight: 8 }} />
                <span className="text-2xs text-apple-secondary" title={h.title}>{h.date?.slice(5)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Improvement Plan */}
      {data.improvement_plan && data.improvement_plan.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-apple-text">AI 提升计划</h3>
          {data.improvement_plan.map((plan, i) => (
            <div key={i} className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-apple-text">{plan.dimension}</span>
                <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                  plan.level.includes('优秀') ? 'bg-green-50 text-green-600' :
                  plan.level.includes('中等') ? 'bg-blue-50 text-blue-600' :
                  'bg-orange-50 text-orange-600'
                }`}>{plan.level}</span>
              </div>
              <ul className="space-y-2">
                {plan.suggestions.map((s, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm text-apple-text">
                    <span className="text-apple-accent mt-1">•</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
