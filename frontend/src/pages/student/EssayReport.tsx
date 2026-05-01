import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, Sparkles, AlertTriangle, Lightbulb, FileText } from 'lucide-react'
import api from '../../api/client'
import type { Essay, EssayReport } from '../../types'

export default function EssayReportPage() {
  const { id } = useParams<{ id: string }>()
  const [essay, setEssay] = useState<Essay | null>(null)
  const [report, setReport] = useState<EssayReport | null>(null)
  const [loading, setLoading] = useState(true)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!id) return
    loadData()
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [id])

  const loadData = async () => {
    if (!id) return
    try {
      const [essayRes, reportRes] = await Promise.all([
        api.get(`/essays/${id}`),
        api.get(`/essays/${id}/report`),
      ])
      const e = essayRes.data
      const r = reportRes.data
      setEssay(e)
      setReport(r)
      setLoading(false)

      // 如果正在批改中，启动轮询
      if (e.status === 'grading' && !r) {
        startPolling()
      }
    } catch {
      setLoading(false)
    }
  }

  const startPolling = () => {
    if (pollRef.current) return
    pollRef.current = setInterval(async () => {
      try {
        const { data } = await api.get(`/essays/${id}/report`)
        if (data && data.total_score !== undefined) {
          setReport(data)
          if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null }
          // 同时更新 essay 状态
          setEssay((prev) => prev ? { ...prev, status: 'graded' } : null)
        }
      } catch { /* ignore poll errors */ }
    }, 3000)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 animate-spin text-apple-accent" />
      </div>
    )
  }

  if (!essay) {
    return (
      <div className="text-center py-24">
        <p className="text-apple-secondary">作文未找到</p>
        <Link to="/student/history" className="text-apple-accent hover:underline mt-2 inline-block">返回历史</Link>
      </div>
    )
  }

  if (essay.status === 'grading' && !report) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-apple-accent" />
        <p className="text-apple-text font-medium">AI 正在批改中...</p>
        <p className="text-sm text-apple-secondary">预计需要 15-30 秒</p>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="text-center py-24">
        <p className="text-apple-secondary">批改报告尚未生成</p>
        <p className="text-sm text-apple-secondary mt-1">请稍后刷新</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-12">
      <Link to="/student/history" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">返回</span>
      </Link>

      <h2 className="text-2xl font-bold text-apple-text tracking-tight">{essay.title || '未命名作文'}</h2>

      {/* Original Essay */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-5 h-5 text-apple-accent" />
          <h3 className="font-semibold text-apple-text">作文原文</h3>
          <span className="text-xs text-apple-secondary">{essay.word_count} 字</span>
        </div>
        <p className="text-sm text-apple-text leading-relaxed whitespace-pre-wrap">{essay.content}</p>
      </div>

      {/* Score Card */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-8 text-center">
        <div className="text-xs font-semibold text-apple-secondary tracking-wide uppercase mb-2">总分</div>
        <div className="text-7xl font-bold text-apple-text tracking-tighter">{report.total_score}</div>
        <div className="text-sm text-apple-secondary mt-1">满分 45</div>
        <div className="flex justify-center gap-6 mt-6 pt-6 border-t border-apple-divider">
          {[
            { label: '立意 / 10', value: report.score_thesis ?? 0, color: '#007AFF' },
            { label: '内容 / 15', value: report.score_content, color: '#34C759' },
            { label: '语言 / 10', value: report.score_language, color: '#FF9500' },
            { label: '结构 / 5', value: report.score_structure, color: '#AF52DE' },
            { label: '文面 / 5', value: report.score_penmanship, color: '#FF3B30' },
          ].map(({ label, value, color }) => (
            <div key={label} className="text-center">
              <div className="text-xl font-semibold" style={{ color }}>{value}</div>
              <div className="text-2xs text-apple-secondary">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Basic Errors */}
      {report.basic_errors && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-apple-orange" />
            <h3 className="font-semibold text-apple-text">基础检测</h3>
          </div>
          <div className="flex gap-4">
            <div className="flex-1 bg-red-50 rounded-2xl p-4 text-center">
              <div className="text-2xl font-bold text-apple-red">{report.basic_errors.typos?.length || 0}</div>
              <div className="text-xs text-apple-secondary mt-1">错别字</div>
            </div>
            <div className="flex-1 bg-orange-50 rounded-2xl p-4 text-center">
              <div className="text-2xl font-bold text-apple-orange">{report.basic_errors.grammar?.length || 0}</div>
              <div className="text-xs text-apple-secondary mt-1">病句</div>
            </div>
            <div className="flex-1 bg-green-50 rounded-2xl p-4 text-center">
              <div className="text-2xl font-bold text-apple-green">{report.basic_errors.punctuation?.length || 0}</div>
              <div className="text-xs text-apple-secondary mt-1">标点错误</div>
            </div>
          </div>
        </div>
      )}

      {/* Paragraph Reviews */}
      {report.paragraph_reviews && report.paragraph_reviews.length > 0 && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">逐段点评</h3>
          </div>
          <div className="space-y-3">
            {report.paragraph_reviews.map((review, i) => (
              <div key={i} className="bg-[#F2F2F7] rounded-2xl p-5 border-l-4 border-apple-accent">
                <div className="text-xs text-apple-secondary mb-1.5">原文</div>
                <div className="text-sm text-apple-text mb-3 leading-relaxed">{review.original}</div>
                <div className="text-sm text-apple-accent leading-relaxed">{review.comment}</div>
                {review.suggestion && (
                  <div className="text-sm text-apple-green mt-2 leading-relaxed">修改建议：{review.suggestion}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overall Comment */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
        <h3 className="font-semibold text-apple-text mb-3">总评</h3>
        <p className="text-sm text-apple-text leading-relaxed">{report.overall_comment}</p>
      </div>

      {/* Suggestions */}
      {report.suggestions && report.suggestions.length > 0 && (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">提升建议</h3>
          </div>
          <div className="space-y-3">
            {report.suggestions.map((s, i) => (
              <div key={i} className="flex items-start gap-3 bg-[#F2F2F7] rounded-2xl p-4">
                <div className="w-6 h-6 bg-apple-accent text-white rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0">
                  {i + 1}
                </div>
                <p className="text-sm text-apple-text leading-relaxed">{s}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-center pt-6">
        <Link
          to="/student/write"
          className="inline-flex items-center gap-2 px-6 py-3 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 transition-all shadow-lg shadow-blue-500/20"
        >
          <PenLineIcon className="w-4 h-4" />
          再写一篇
        </Link>
      </div>
    </div>
  )
}

function PenLineIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zM19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
    </svg>
  )
}
