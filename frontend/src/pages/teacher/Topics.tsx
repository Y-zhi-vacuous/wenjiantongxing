import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import api from '../../api/client'
import type { EssayTopic } from '../../types'

export default function Topics() {
  const [topics, setTopics] = useState<EssayTopic[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ title: '', type: '命题', genre: '记叙文', difficulty: 3, tips: '', word_requirement: 600, time_minutes: 45, extra_requirements: '' })
  const [loading, setLoading] = useState(true)

  const fetchTopics = () => {
    api.get('/topics').then(({ data }) => {
      setTopics(data.topics || data)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchTopics() }, [])

  const handleAdd = async () => {
    await api.post('/topics', form)
    setForm({ title: '', type: '命题', genre: '记叙文', difficulty: 3, tips: '', word_requirement: 600, time_minutes: 45, extra_requirements: '' })
    setShowAdd(false)
    fetchTopics()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">题库管理</h2>
          <p className="text-apple-secondary mt-1">管理作文题目</p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-apple-xs font-medium hover:bg-blue-600 transition-all"
        >
          <Plus className="w-4 h-4" />
          添加题目
        </button>
      </div>

      {showAdd && (
        <div className="bg-white rounded-apple shadow-apple p-6 space-y-4">
          <h3 className="font-semibold text-apple-text">添加新题目</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">题目</label>
              <input type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
                     className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all"
                     placeholder="作文题目" />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">类型</label>
              <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all">
                {['命题', '半命题', '材料', '话题'].map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">体裁</label>
              <select value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all">
                {['记叙文', '议论文'].map((g) => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">难度 ({form.difficulty})</label>
              <input type="range" min="1" max="5" value={form.difficulty}
                     onChange={(e) => setForm({ ...form, difficulty: Number(e.target.value) })}
                     className="w-full accent-apple-accent" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">审题提示</label>
            <input type="text" value={form.tips} onChange={(e) => setForm({ ...form, tips: e.target.value })}
                   className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all"
                   placeholder="可选：给学生一些审题提示" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">字数要求</label>
              <input type="number" value={form.word_requirement} onChange={(e) => setForm({ ...form, word_requirement: Number(e.target.value) })}
                     className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all" />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">建议用时(分钟)</label>
              <input type="number" value={form.time_minutes} onChange={(e) => setForm({ ...form, time_minutes: Number(e.target.value) })}
                     className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">附加要求</label>
            <input type="text" value={form.extra_requirements} onChange={(e) => setForm({ ...form, extra_requirements: e.target.value })}
                   className="w-full px-4 py-2.5 rounded-apple-xs border border-apple-divider bg-apple-bg focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all"
                   placeholder="如：不少于600字；不得出现真实校名、人名" />
          </div>
          <div className="flex gap-3">
            <button onClick={handleAdd} className="px-6 py-2.5 bg-apple-accent text-white rounded-apple-xs font-medium hover:bg-blue-600 transition-all">添加</button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2.5 text-apple-secondary hover:text-apple-text transition-all">取消</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-apple-secondary">加载中...</div>
      ) : (
        <div className="space-y-3">
          {topics.map((t) => (
            <div key={t.id} className="bg-white rounded-apple shadow-apple p-5">
              <h4 className="font-medium text-apple-text">{t.title}</h4>
              <div className="flex gap-2 mt-1.5">
                <span className="text-xs bg-apple-bg px-2 py-0.5 rounded text-apple-secondary">{t.type}</span>
                <span className="text-xs bg-apple-bg px-2 py-0.5 rounded text-apple-secondary">{t.genre}</span>
                <span className="text-xs bg-apple-bg px-2 py-0.5 rounded text-apple-secondary">难度 {'★'.repeat(t.difficulty)}</span>
                <span className="text-xs bg-apple-bg px-2 py-0.5 rounded text-apple-secondary">{t.source === 'system' ? '系统' : '自定义'}</span>
              </div>
              {t.tips && <p className="text-sm text-apple-secondary mt-2 italic">{t.tips}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
