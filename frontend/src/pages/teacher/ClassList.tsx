import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Users, ArrowRight } from 'lucide-react'
import api from '../../api/client'
import type { ClassInfo } from '../../types'

export default function ClassList() {
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchClasses = () => {
    api.get('/classes').then(({ data }) => {
      setClasses(data.classes || data)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchClasses() }, [])

  const handleCreate = async () => {
    if (!newName.trim()) return
    await api.post('/classes', { name: newName })
    setNewName('')
    setShowCreate(false)
    fetchClasses()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">班级管理</h2>
          <p className="text-apple-secondary mt-1">管理你的教学班级</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-apple-xs font-medium hover:bg-blue-600 transition-all"
        >
          <Plus className="w-4 h-4" />
          创建班级
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-apple shadow-apple p-6 space-y-4">
          <h3 className="font-semibold text-apple-text">创建新班级</h3>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="w-full px-4 py-3 rounded-apple-xs border border-apple-divider bg-apple-bg text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"
            placeholder="班级名称，如：九(3)班"
          />
          <div className="flex gap-3">
            <button onClick={handleCreate} className="px-6 py-2.5 bg-apple-accent text-white rounded-apple-xs font-medium hover:bg-blue-600 transition-all">创建</button>
            <button onClick={() => setShowCreate(false)} className="px-6 py-2.5 text-apple-secondary hover:text-apple-text transition-all">取消</button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-apple-secondary">加载中...</div>
      ) : classes.length === 0 ? (
        <div className="bg-white rounded-apple shadow-apple p-12 text-center">
          <Users className="w-10 h-10 mx-auto mb-3 text-apple-disabled" />
          <p className="text-apple-secondary">暂无班级，点击上方按钮创建</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {classes.map((c) => (
            <Link
              key={c.id}
              to={`/teacher/classes/${c.id}`}
              className="bg-white rounded-apple shadow-apple p-5 hover:shadow-apple-lg transition-all hover:-translate-y-0.5 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <Users className="w-5 h-5 text-apple-accent" />
                <div>
                  <h4 className="font-medium text-apple-text">{c.name}</h4>
                  <p className="text-sm text-apple-secondary">创建于 {new Date(c.created_at).toLocaleDateString('zh-CN')}</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-apple-disabled" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
