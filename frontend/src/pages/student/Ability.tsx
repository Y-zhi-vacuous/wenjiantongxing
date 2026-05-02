import { useEffect, useState } from 'react'
import { TrendingUp, Target, Sparkles, AlertCircle } from 'lucide-react'
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
  vocabulary_stats: any
  last_updated: string
  message?: string
}

const dimLabels: Record<string, { label: string; color: string }> = {
  content: { label: '内容能力', color: '#FF3B30' },
  language: { label: '语言能力', color: '#34C759' },
  structure: { label: '结构能力', color: '#FF9500' },
  penmanship: { label: '文面能力', color: '#AF52DE' },
}

export default function Ability() {
  const [data, setData] = useState<AbilityData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/ability/me').then(({ data }) => setData(data)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-24 text-apple-secondary">加载中...</div>

  if (!data || data.essay_count === 0) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">能力画像</h2>
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06),0_4px_12px_rgba(0,0,0,0.04)] p-12 text-center">
          <Sparkles className="w-12 h-12 mx-auto mb-4 text-apple-disabled" />
          <p className="text-apple-text font-medium mb-2">还没有数据</p>
          <p className="text-sm text-apple-secondary">提交第一篇作文并获得 AI 批改后，将生成你的专属能力画像</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">能力画像</h2>
        <p className="text-apple-secondary mt-1">AI 根据你的 {data.essay_count} 篇作文生成的分析报告</p>
      </div>

      {/* Overall Score */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06),0_4px_12px_rgba(0,0,0,0.04)] p-8 text-center">
        <div className="text-xs font-semibold text-apple-secondary tracking-wide uppercase mb-2">综合均分</div>
        <div className="text-7xl font-bold text-apple-text tracking-tighter">{data.overall_score}</div>
        <div className="text-sm text-apple-secondary mt-1">满分 50 · 共 {data.essay_count} 篇</div>
      </div>

      {/* Four Dimensions */}
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(dimLabels).map(([key, { label, color }]) => {
          const score = data.abilities[key as keyof typeof data.abilities] || 0
          return (
            <div key={key} className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-apple-text">{label}</span>
                <span className="text-2xl font-bold" style={{ color }}>{score}</span>
              </div>
              <div className="h-2 bg-apple-bg rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-700 ease-out" style={{ width: `${score}%`, background: color }} />
              </div>
              <div className="flex justify-between mt-1.5 text-2xs text-apple-secondary">
                <span>0</span><span>100</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-5 h-5 text-apple-green" />
            <h3 className="font-semibold text-apple-text">优势领域</h3>
          </div>
          <div className="space-y-2">
            {data.strengths?.map((s) => (
              <div key={s} className="bg-green-50 rounded-xl px-4 py-2.5 text-sm text-green-700">{s}</div>
            ))}
          </div>
        </div>
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5 text-apple-orange" />
            <h3 className="font-semibold text-apple-text">待提升领域</h3>
          </div>
          <div className="space-y-2">
            {data.weaknesses?.map((w) => (
              <div key={w} className="bg-orange-50 rounded-xl px-4 py-2.5 text-sm text-orange-700">{w}</div>
            ))}
          </div>
        </div>
      </div>

      {/* Score History */}
      {data.score_history && data.score_history.length > 0 && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">分数趋势</h3>
          </div>
          <div className="flex items-end gap-3 h-40">
            {data.score_history.map((h, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
                <span className="text-xs font-semibold text-apple-text">{h.total_score}</span>
                <div
                  className="w-full bg-apple-accent rounded-t-lg transition-all hover:bg-blue-600 min-h-[4px]"
                  style={{ height: `${Math.max((h.total_score / 45) * 100, 4)}%` }}
                />
                <span className="text-2xs text-apple-secondary truncate max-w-full" title={h.title}>
                  {h.date?.slice(5)}
                </span>
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
            <div key={i} className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.06)] p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-apple-text">{plan.dimension}</span>
                <span className={`text-xs font-medium px-3 py-1 rounded-full ${
                  plan.level === '优秀' ? 'bg-green-50 text-green-600' :
                  plan.level === '中等偏上' ? 'bg-blue-50 text-blue-600' :
                  'bg-orange-50 text-orange-600'
                }`}>{plan.level}</span>
              </div>
              <ul className="space-y-2">
                {plan.suggestions.map((s, j) => (
                  <li key={j} className="flex items-start gap-2 text-sm text-apple-text">
                    <span className="text-apple-accent mt-1">•</span>
                    {s}
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
