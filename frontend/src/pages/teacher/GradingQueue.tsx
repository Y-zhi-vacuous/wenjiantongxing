import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, FileText, CheckCircle2, AlertCircle } from 'lucide-react'
import api from '../../api/client'
import type { Essay } from '../../types'

export default function GradingQueue() {
  const [essays, setEssays] = useState<Essay[]>([])
  const [loading, setLoading] = useState(true)
  const [gradingAll, setGradingAll] = useState(false)
  const [gradingIds, setGradingIds] = useState<Set<number>>(new Set())
  const [message, setMessage] = useState('')

  const fetchUngraded = () => {
    setLoading(true)
    api.get('/essays/list/ungraded')
      .then(({ data }) => setEssays(data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchUngraded() }, [])

  // Auto-refresh every 10s
  useEffect(() => {
    const interval = setInterval(fetchUngraded, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleGradeOne = async (essayId: number) => {
    setGradingIds((prev) => new Set(prev).add(essayId))
    try {
      await api.post(`/essays/${essayId}/grade`)
      setMessage(`作文 #${essayId} 批改已开始`)
      // Poll until done
      const poll = setInterval(async () => {
        const { data: essayData } = await api.get(`/essays/${essayId}`)
        if (essayData.status === 'graded') {
          clearInterval(poll)
          setGradingIds((prev) => { const next = new Set(prev); next.delete(essayId); return next })
          fetchUngraded()
        }
      }, 3000)
    } catch (err: any) {
      alert(err.response?.data?.detail || '批改请求失败')
      setGradingIds((prev) => { const next = new Set(prev); next.delete(essayId); return next })
    }
  }

  const handleGradeAll = async () => {
    if (!confirm(`确认批改全部 ${essays.length} 篇作文？将逐篇串行处理。`)) return
    setGradingAll(true)
    try {
      const { data } = await api.post('/essays/grade-all')
      setMessage(data.message || '批改已启动')
    } catch (err: any) {
      alert(err.response?.data?.detail || '批量批改请求失败')
    }
    setGradingAll(false)
  }

  const submittedCount = essays.filter(e => e.status === 'submitted' || e.status === 'draft').length

  if (loading) return <div className="flex items-center justify-center py-24"><Loader2 className="w-8 h-8 animate-spin text-apple-accent" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">待批改作文</h2>
          <p className="text-apple-secondary mt-1">
            {submittedCount > 0
              ? `共 ${submittedCount} 篇待批改`
              : '全部已批改'}
          </p>
        </div>
        {submittedCount > 0 && (
          <button onClick={handleGradeAll} disabled={gradingAll}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 transition-all disabled:opacity-50 shadow-lg shadow-blue-500/20">
            {gradingAll ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
            {gradingAll ? '启动中...' : '一键全部批改'}
          </button>
        )}
      </div>

      {message && (
        <div className="p-3 rounded-xl bg-green-50 text-green-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {message}
          <button onClick={() => setMessage('')} className="ml-auto text-green-500 hover:text-green-700">✕</button>
        </div>
      )}

      {essays.length === 0 ? (
        <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-12 text-center">
          <CheckCircle2 className="w-12 h-12 text-apple-green mx-auto mb-3" />
          <p className="text-apple-text font-medium">所有作文已完成批改</p>
          <p className="text-sm text-apple-secondary mt-1">学生提交新作文后将会出现在这里</p>
        </div>
      ) : (
        <div className="space-y-3">
          {essays.map((essay) => {
            const isGrading = gradingIds.has(essay.id)
            return (
              <div key={essay.id}
                   className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-5 flex items-center gap-4">
                <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-apple-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-apple-text text-sm truncate">{essay.title || '未命名作文'}</h4>
                  <p className="text-xs text-apple-secondary mt-0.5">
                    {essay.word_count} 字 · {essay.topic?.title?.slice(0, 20)} · 提交于 {new Date(essay.submitted_at).toLocaleDateString('zh-CN')}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link to={`/teacher/essay/${essay.id}`}
                        className="px-4 py-2 rounded-xl border border-apple-divider text-apple-text text-sm hover:bg-[#F2F2F7] transition-all">
                    查看
                  </Link>
                  <button onClick={() => handleGradeOne(essay.id)} disabled={isGrading}
                          className="px-4 py-2 bg-apple-accent text-white rounded-xl text-sm font-medium hover:bg-blue-600 transition-all disabled:opacity-50">
                    {isGrading ? '批改中...' : '批改'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
