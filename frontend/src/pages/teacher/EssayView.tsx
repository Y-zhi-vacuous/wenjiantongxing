import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, FileText, Sparkles, Lightbulb, GraduationCap } from 'lucide-react'
import api from '../../api/client'
import type { Essay, EssayReport } from '../../types'

export default function EssayView() {
  const { id } = useParams<{ id: string }>()
  const [essay, setEssay] = useState<Essay | null>(null)
  const [report, setReport] = useState<EssayReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [grading, setGrading] = useState(false)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchData = () => {
    if (!id) return
    Promise.all([
      api.get(`/essays/${id}`),
      api.get(`/essays/${id}/report`),
    ]).then(([essayRes, reportRes]) => {
      setEssay(essayRes.data)
      setReport(reportRes.data)
    }).finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchData()
    return () => { if (pollingRef.current) clearInterval(pollingRef.current) }
  }, [id])

  const handleGrade = async () => {
    if (!id) return
    setGrading(true)
    try {
      await api.post(`/essays/${id}/grade`)
      // Poll for report
      pollingRef.current = setInterval(async () => {
        const { data: essayData } = await api.get(`/essays/${id}`)
        if (essayData.status === 'graded') {
          clearInterval(pollingRef.current!)
          pollingRef.current = null
          fetchData()
          setGrading(false)
        }
      }, 3000)
    } catch (err: any) {
      alert(err.response?.data?.detail || '批改请求失败')
      setGrading(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center py-24"><Loader2 className="w-8 h-8 animate-spin text-apple-accent" /></div>
  if (!essay) return <div className="text-center py-12"><p className="text-apple-secondary">作文未找到</p></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/teacher/grading" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text transition-colors">
          <ArrowLeft className="w-4 h-4" /><span className="text-sm">返回列表</span>
        </Link>
        {(essay.status === 'submitted' || essay.status === 'draft') && (
          <button onClick={handleGrade} disabled={grading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 transition-all disabled:opacity-50 shadow-lg shadow-blue-500/20">
            {grading ? <Loader2 className="w-4 h-4 animate-spin" /> : <GraduationCap className="w-4 h-4" />}
            {grading ? '批改中...' : '批改此作文'}
          </button>
        )}
        {essay.status === 'grading' && (
          <span className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-50 text-yellow-700 rounded-full text-sm font-medium">
            <Loader2 className="w-4 h-4 animate-spin" /> 批改进行中...
          </span>
        )}
      </div>

      <h2 className="text-2xl font-bold text-apple-text tracking-tight">{essay.title || '未命名作文'}</h2>
      <p className="text-sm text-apple-secondary">{essay.word_count} 字 · 状态：{essay.status === 'graded' ? '已批改' : essay.status === 'grading' ? '批改中' : '待批改'}</p>

      {/* Original Essay */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-5 h-5 text-apple-accent" />
          <h3 className="font-semibold text-apple-text">作文原文</h3>
        </div>
        <p className="text-sm text-apple-text leading-relaxed whitespace-pre-wrap">{essay.content}</p>
      </div>

      {report ? (
        <>
          <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-8 text-center">
            <div className="text-xs font-semibold text-apple-secondary tracking-wide uppercase mb-2">总分</div>
            <div className="text-7xl font-bold text-apple-text tracking-tighter">{report.total_score}</div>
            <div className="text-sm text-apple-secondary mt-1">满分 45 · {report.model_used || 'AI'}</div>
            {report.topic_match && (
              <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium mt-3 ${
                report.topic_match.includes('离题') ? 'bg-red-50 text-red-600' :
                report.topic_match.includes('偏题') ? 'bg-orange-50 text-orange-600' :
                'bg-green-50 text-green-600'
              }`}>
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
                {report.topic_match}
              </div>
            )}
            {report.level && <div className="text-sm text-apple-secondary mt-1">{report.level}</div>}
            {report.deduction_reason && report.deduction_reason !== '无' && (
              <div className="text-xs text-red-500 mt-1">扣分原因：{report.deduction_reason}</div>
            )}
            <div className="flex justify-center gap-8 mt-6 pt-6 border-t border-apple-divider">
              {[
                { label: '内容 / 15', value: report.score_content },
                { label: '语言 / 15', value: report.score_language },
                { label: '结构 / 10', value: report.score_structure },
                { label: '文面 / 5', value: report.score_penmanship },
              ].map(({ label, value }) => (
                <div key={label} className="text-center">
                  <div className="text-xl font-semibold text-apple-text">{value}</div>
                  <div className="text-xs text-apple-secondary">{label}</div>
                </div>
              ))}
            </div>
          </div>

          {report.paragraph_reviews && report.paragraph_reviews.length > 0 && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-apple-accent" />
                <h3 className="font-semibold text-apple-text">逐段点评</h3>
              </div>
              {report.paragraph_reviews.map((r, i) => (
                <div key={i} className="bg-[#F2F2F7] rounded-2xl p-4 mb-2 border-l-4 border-apple-accent">
                  <div className="text-xs text-apple-secondary mb-1">原文</div>
                  <div className="text-sm text-apple-text mb-2">{r.original}</div>
                  <div className="text-sm text-apple-accent">{r.comment}</div>
                  {r.suggestion && <div className="text-sm text-apple-green mt-1">建议：{r.suggestion}</div>}
                </div>
              ))}
            </div>
          )}

          <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
            <h3 className="font-semibold text-apple-text mb-3">总评</h3>
            <p className="text-sm text-apple-text leading-relaxed">{report.overall_comment}</p>
          </div>

          {report.suggestions && report.suggestions.length > 0 && (
            <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-apple-accent" />
                <h3 className="font-semibold text-apple-text">提升建议</h3>
              </div>
              {report.suggestions.map((s, i) => (
                <div key={i} className="flex items-start gap-3 bg-[#F2F2F7] rounded-2xl p-4 mb-2">
                  <div className="w-6 h-6 bg-apple-accent text-white rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0">{i + 1}</div>
                  <p className="text-sm text-apple-text">{s}</p>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-12 text-center">
          <p className="text-apple-secondary">该作文尚未批改</p>
          <p className="text-xs text-apple-disabled mt-2">点击上方「批改此作文」按钮开始批改</p>
        </div>
      )}
    </div>
  )
}
