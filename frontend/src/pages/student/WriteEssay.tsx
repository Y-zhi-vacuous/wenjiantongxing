import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Send, Loader2, Image, Keyboard } from 'lucide-react'
import api from '../../api/client'
import type { EssayTopic } from '../../types'

const cardClass = "bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"
const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"

type Tab = 'write' | 'upload' | 'image'

export default function WriteEssay() {
  const navigate = useNavigate()
  const [topics, setTopics] = useState<EssayTopic[]>([])
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState<Tab>('write')

  useEffect(() => {
    api.get('/topics').then(({ data }) => setTopics(data.topics || data))
  }, [])

  const handleSubmit = async () => {
    if (!selectedTopic) return
    setLoading(true)
    try {
      if (tab === 'write') {
        await api.post('/essays', { topic_id: selectedTopic, title: title || '未命名', content })
      } else if (tab === 'image' && file) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('topic_id', String(selectedTopic))
        formData.append('title', title || '手写作文-' + file.name)
        await api.post('/essays/upload-image', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else if (file) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('topic_id', String(selectedTopic))
        formData.append('title', title || file.name.replace(/\.[^.]+$/, ''))
        await api.post('/essays/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else return
      // v2.0: 不再自动触发批改，改为教师端批改
      navigate('/student/history')
    } finally { setLoading(false) }
  }

  const tabs: { key: Tab; icon: typeof Keyboard; label: string }[] = [
    { key: 'write', icon: Keyboard, label: '在线写作' },
    { key: 'upload', icon: Upload, label: '上传文件' },
    { key: 'image', icon: Image, label: '手写拍照' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">写作文</h2>
          <p className="text-apple-secondary mt-1">选择题目，开始写作</p>
        </div>
      </div>

      {/* Topic Selection */}
      <div className={`${cardClass} p-6`}>
        <h3 className="font-semibold text-apple-text mb-4">选择题目</h3>
        <div className="grid gap-2 max-h-80 overflow-y-auto">
          {topics.map((topic) => (
            <button
              key={topic.id}
              onClick={() => setSelectedTopic(topic.id)}
              className={`text-left p-4 rounded-2xl border transition-all duration-200 ${
                selectedTopic === topic.id
                  ? 'border-apple-accent bg-blue-50/50 shadow-sm'
                  : 'border-transparent hover:bg-[#F2F2F7]'
              }`}
            >
              <div className="font-medium text-apple-text text-sm">{topic.title}</div>
              <div className="flex gap-2 mt-1.5">
                <span className="text-xs text-apple-secondary bg-white/80 rounded-lg px-2.5 py-0.5">{topic.type}</span>
                <span className="text-xs text-apple-secondary bg-white/80 rounded-lg px-2.5 py-0.5">{topic.genre}</span>
                <span className="text-xs text-apple-secondary bg-white/80 rounded-lg px-2.5 py-0.5">
                  {'★'.repeat(topic.difficulty)}
                </span>
                {topic.source === 'teacher' && <span className="text-xs text-apple-accent bg-blue-50 rounded-lg px-2.5 py-0.5">教师</span>}
              </div>
              {selectedTopic === topic.id && (
                <div className="mt-3 pt-3 border-t border-apple-divider space-y-2">
                  {topic.tips && (
                    <p className="text-sm text-apple-secondary leading-relaxed">💡 {topic.tips}</p>
                  )}
                  <div className="flex gap-4 text-xs text-apple-secondary">
                    <span>📝 {topic.word_requirement}字</span>
                    <span>⏱ {topic.time_minutes}分钟</span>
                  </div>
                  {topic.extra_requirements && (
                    <p className="text-xs text-apple-disabled leading-relaxed">📋 {topic.extra_requirements}</p>
                  )}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Writing Area */}
      <div className={`${cardClass} p-6`}>
        <div className="flex gap-1 mb-6 bg-[#F2F2F7] p-1 rounded-2xl">
          {tabs.map(({ key, icon: Icon, label }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                tab === key
                  ? 'bg-white text-apple-text shadow-[0_1px_3px_rgba(0,0,0,0.08)]'
                  : 'text-apple-secondary hover:text-apple-text'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        <div>
          <label className="block text-sm font-medium text-apple-text mb-1.5">作文标题</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
                 className={inputClass} placeholder="输入标题（可选）" />
        </div>

        {tab === 'write' ? (
          <div className="mt-4 space-y-2">
            <textarea
              value={content} onChange={(e) => setContent(e.target.value)}
              rows={16}
              className="w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all resize-none text-sm leading-relaxed"
              placeholder="开始写作..."
            />
            <p className="text-xs text-apple-secondary text-right">{content.length} 字</p>
          </div>
        ) : tab === 'image' ? (
          <div className="mt-4">
            <div className="border-2 border-dashed border-apple-divider rounded-2xl p-16 text-center hover:border-apple-accent/40 transition-all cursor-pointer group"
                 onClick={() => document.getElementById('image-upload')?.click()}>
              {file ? (
                <div>
                  <img src={URL.createObjectURL(file)} alt="preview" className="max-h-48 mx-auto rounded-xl shadow-sm mb-3" />
                  <p className="font-medium text-apple-text">{file.name}</p>
                  <p className="text-sm text-apple-secondary">{(file.size / 1024).toFixed(1)} KB · 点击更换</p>
                </div>
              ) : (
                <div className="group-hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <Image className="w-8 h-8 text-apple-accent" />
                  </div>
                  <p className="text-apple-text font-medium">拍照上传手写作文</p>
                  <p className="text-sm text-apple-secondary mt-1">支持 JPG、PNG 格式</p>
                </div>
              )}
              <input id="image-upload" type="file" accept="image/*" className="hidden"
                     onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </div>
          </div>
        ) : (
          <div className="mt-4">
            <div className="border-2 border-dashed border-apple-divider rounded-2xl p-16 text-center hover:border-apple-accent/40 transition-all cursor-pointer group"
                 onClick={() => document.getElementById('file-upload')?.click()}>
              {file ? (
                <div>
                  <FileText className="w-10 h-10 mx-auto mb-2 text-apple-accent" />
                  <p className="font-medium text-apple-text">{file.name}</p>
                  <p className="text-sm text-apple-secondary">{(file.size / 1024).toFixed(1)} KB · 点击更换</p>
                </div>
              ) : (
                <div className="group-hover:scale-105 transition-transform">
                  <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-3">
                    <Upload className="w-8 h-8 text-apple-accent" />
                  </div>
                  <p className="text-apple-text font-medium">上传作文文件</p>
                  <p className="text-sm text-apple-secondary mt-1">支持 .docx .pdf 格式</p>
                </div>
              )}
              <input id="file-upload" type="file" accept=".docx,.pdf,.doc" className="hidden"
                     onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </div>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading || !selectedTopic || (tab === 'write' && !content.trim()) || ((tab === 'upload' || tab === 'image') && !file)}
          className="w-full mt-6 py-3.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all duration-200 disabled:opacity-30 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          {loading ? '提交中...' : '提交作文（等待老师批改）'}
        </button>
      </div>
    </div>
  )
}
