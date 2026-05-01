import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import api from '../../api/client'
import type { Essay, EssayReport } from '../../types'

export default function EssayView() {
  const { id } = useParams<{ id: string }>()
  const [essay, setEssay] = useState<Essay | null>(null)
  const [report, setReport] = useState<EssayReport | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.get(`/essays/${id}`),
      api.get(`/essays/${id}/report`),
    ]).then(([essayRes, reportRes]) => {
      setEssay(essayRes.data)
      setReport(reportRes.data)
    }).finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex items-center justify-center py-24"><Loader2 className="w-8 h-8 animate-spin text-apple-accent" /></div>

  if (!essay) {
    return <div className="text-center py-12"><p className="text-apple-secondary">作文未找到</p></div>
  }

  return (
    <div className="space-y-6">
      <Link to="/teacher/classes" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text transition-colors">
        <ArrowLeft className="w-4 h-4" /><span className="text-sm">返回</span>
      </Link>

      <h2 className="text-2xl font-bold text-apple-text tracking-tight">{essay.title || '未命名作文'}</h2>

      {report ? (
        <>
          <div className="bg-white rounded-apple shadow-apple p-8 text-center">
            <div className="text-xs font-semibold text-apple-secondary tracking-wide uppercase mb-2">总分</div>
            <div className="text-7xl font-bold text-apple-text tracking-tighter">{report.total_score}</div>
            <div className="flex justify-center gap-8 mt-6 pt-6 border-t border-apple-divider">
              {[
                { label: '内容 / 20', value: report.score_content },
                { label: '语言 / 15', value: report.score_language },
                { label: '结构 / 10', value: report.score_structure },
                { label: '卷面 / 5', value: report.score_penmanship },
              ].map(({ label, value }) => (
                <div key={label} className="text-center">
                  <div className="text-xl font-semibold text-apple-text">{value}</div>
                  <div className="text-xs text-apple-secondary">{label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white rounded-apple shadow-apple p-6">
            <h3 className="font-semibold text-apple-text mb-3">总评</h3>
            <p className="text-sm text-apple-text leading-relaxed">{report.overall_comment}</p>
          </div>
          {report.suggestions && report.suggestions.length > 0 && (
            <div className="bg-white rounded-apple shadow-apple p-6">
              <h3 className="font-semibold text-apple-text mb-3">提升建议</h3>
              <ul className="space-y-2">
                {report.suggestions.map((s, i) => (
                  <li key={i} className="text-sm text-apple-text flex gap-2">
                    <span className="text-apple-accent font-semibold">{i + 1}.</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-apple shadow-apple p-6">
          <h3 className="font-semibold text-apple-text mb-3">作文原文</h3>
          <p className="text-sm text-apple-text leading-relaxed whitespace-pre-wrap">{essay.content}</p>
        </div>
      )}
    </div>
  )
}
