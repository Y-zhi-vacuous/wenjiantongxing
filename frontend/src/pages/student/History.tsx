import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Search } from 'lucide-react'
import api from '../../api/client'
import type { Essay } from '../../types'

export default function History() {
  const [essays, setEssays] = useState<Essay[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/essays').then(({ data }) => {
      setEssays(data.essays || data)
    }).finally(() => setLoading(false))
  }, [])

  const statusLabel = (s: string) => {
    switch (s) {
      case 'graded': return { text: '已批改', cls: 'bg-apple-green/10 text-apple-green' }
      case 'grading': return { text: '批改中', cls: 'bg-apple-orange/10 text-apple-orange' }
      default: return { text: '待批改', cls: 'bg-apple-disabled/20 text-apple-secondary' }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">写作历史</h2>
        <p className="text-apple-secondary mt-1">所有提交的作文</p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-apple-secondary">加载中...</div>
      ) : essays.length === 0 ? (
        <div className="bg-white rounded-apple shadow-apple p-12 text-center">
          <Search className="w-10 h-10 mx-auto mb-3 text-apple-disabled" />
          <p className="text-apple-secondary">暂无作文记录</p>
        </div>
      ) : (
        <div className="space-y-3">
          {essays.map((essay) => {
            const s = statusLabel(essay.status)
            return (
              <Link
                key={essay.id}
                to={`/student/essay/${essay.id}`}
                className="block bg-white rounded-apple shadow-apple p-5 hover:shadow-apple-lg transition-all hover:-translate-y-0.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-apple-disabled" />
                    <div>
                      <h4 className="font-medium text-apple-text">{essay.title || '未命名作文'}</h4>
                      <p className="text-sm text-apple-secondary">
                        {essay.word_count} 字 · {essay.topic?.title} · {new Date(essay.submitted_at).toLocaleDateString('zh-CN')}
                      </p>
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-3 py-1 rounded-full ${s.cls}`}>{s.text}</span>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
