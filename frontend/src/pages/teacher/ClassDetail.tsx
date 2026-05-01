import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, UserPlus, FileText, Target, Download, Upload, FileSpreadsheet, ChevronRight } from 'lucide-react'
import api from '../../api/client'
import { API_BASE_URL } from '../../config'

const cardClass = "bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)]"

export default function ClassDetail() {
  const { id } = useParams<{ id: string }>()
  const [classInfo, setClassInfo] = useState<any>(null)
  const [students, setStudents] = useState<any[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [newStudent, setNewStudent] = useState({ username: '', password: '', display_name: '' })
  const [loading, setLoading] = useState(true)
  const [importMsg, setImportMsg] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)

  const fetchDetail = () => {
    if (!id) return
    Promise.all([
      api.get(`/classes/${id}`),
      api.get(`/classes/${id}/students`),
    ]).then(async ([classRes, studentsRes]) => {
      setClassInfo(classRes.data)
      const list = studentsRes.data.students || studentsRes.data
      // 为每个学生获取能力数据
      const studentsWithAbility = await Promise.all(
        list.map(async (s: any) => {
          try {
            const { data } = await api.get(`/ability/student/${s.id}`)
            return { ...s, ability: data }
          } catch { return s }
        })
      )
      setStudents(studentsWithAbility)
    }).finally(() => setLoading(false))
  }

  useEffect(() => { fetchDetail() }, [id])

  const handleAddStudent = async () => {
    const { username, password, display_name } = newStudent
    if (!username.trim() || !password.trim() || !display_name.trim() || !id) return
    await api.post('/auth/register/student', { username, password, display_name, class_id: Number(id) })
    setNewStudent({ username: '', password: '', display_name: '' })
    setShowAdd(false)
    fetchDetail()
  }

  const downloadTemplate = () => {
    const token = localStorage.getItem('token')
    const a = document.createElement('a')
    a.href = `${API_BASE_URL}/classes/${id}/students/template?token=${token}`
    a.click()
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !id) return
    setImportMsg('导入中...')
    const formData = new FormData()
    formData.append('file', file)
    try {
      const { data } = await api.post(`/classes/${id}/students/import`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setImportMsg(data.message)
      fetchDetail()
    } catch (err: any) {
      setImportMsg(err.response?.data?.detail || '导入失败')
    }
    if (fileInput.current) fileInput.current.value = ''
  }

  const handleExport = () => {
    const token = localStorage.getItem('token')
    const a = document.createElement('a')
    a.href = `${API_BASE_URL}/classes/${id}/students/export?token=${token}`
    a.click()
  }

  if (loading) return <div className="text-center py-24 text-apple-secondary">加载中...</div>

  return (
    <div className="space-y-6">
      <Link to="/teacher/classes" className="inline-flex items-center gap-1.5 text-apple-secondary hover:text-apple-text transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm">返回</span>
      </Link>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-apple-text tracking-tight">{classInfo?.name}</h2>
          <p className="text-apple-secondary mt-1">{students.length} 名学生</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={downloadTemplate}
                  className="flex items-center gap-1.5 px-4 py-2.5 bg-[#F2F2F7] text-apple-text rounded-full font-medium text-sm hover:bg-gray-200 active:scale-[0.97] transition-all">
            <Download className="w-4 h-4" />模板
          </button>
          <label className="flex items-center gap-1.5 px-4 py-2.5 bg-[#F2F2F7] text-apple-text rounded-full font-medium text-sm hover:bg-gray-200 active:scale-[0.97] transition-all cursor-pointer">
            <Upload className="w-4 h-4" />导入
            <input ref={fileInput} type="file" accept=".xlsx" className="hidden" onChange={handleImport} />
          </label>
          <button onClick={handleExport}
                  className="flex items-center gap-1.5 px-4 py-2.5 bg-[#F2F2F7] text-apple-text rounded-full font-medium text-sm hover:bg-gray-200 active:scale-[0.97] transition-all">
            <FileSpreadsheet className="w-4 h-4" />导出
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.97] transition-all duration-200 shadow-lg shadow-blue-500/20"
          >
            <UserPlus className="w-4 h-4" />
            添加学生
          </button>
        </div>
      </div>

      {showAdd && (
        <div className={`${cardClass} p-6 space-y-4`}>
          <h3 className="font-semibold text-apple-text">创建学生账号</h3>
          <p className="text-xs text-apple-secondary">为学生创建登录账号，自动加入当前班级</p>
          <div className="grid grid-cols-2 gap-3">
            <input type="text" value={newStudent.username}
                   onChange={(e) => setNewStudent({ ...newStudent, username: e.target.value })}
                   className="w-full px-4 py-2.5 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all text-sm"
                   placeholder="用户名（登录用）" />
            <input type="text" value={newStudent.password}
                   onChange={(e) => setNewStudent({ ...newStudent, password: e.target.value })}
                   className="w-full px-4 py-2.5 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all text-sm"
                   placeholder="默认密码" />
          </div>
          <input type="text" value={newStudent.display_name}
                 onChange={(e) => setNewStudent({ ...newStudent, display_name: e.target.value })}
                 className="w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 transition-all"
                 placeholder="学生姓名（如：张小明）" />
          <div className="flex gap-3">
            <button onClick={handleAddStudent} className="px-6 py-2.5 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 transition-all">创建账号</button>
            <button onClick={() => setShowAdd(false)} className="px-6 py-2.5 text-apple-secondary hover:text-apple-text transition-all">取消</button>
          </div>
        </div>
      )}

      {importMsg && (
        <div className={`${cardClass} p-4 text-center text-sm ${importMsg.includes('成功') ? 'text-green-600' : importMsg.includes('导入中') ? 'text-apple-accent' : 'text-red-500'}`}>
          {importMsg}
        </div>
      )}

      {students.length === 0 ? (
        <div className={`${cardClass} p-16 text-center`}>
          <FileText className="w-10 h-10 mx-auto mb-3 text-apple-disabled" />
          <p className="text-apple-secondary">暂无学生</p>
        </div>
      ) : (
        <div className="space-y-3">
          {students.map((s: any) => (
            <div key={s.id} className={`${cardClass} p-5`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl flex items-center justify-center">
                    <span className="text-apple-accent font-bold text-lg">{s.display_name?.[0] || s.username?.[0] || '?'}</span>
                  </div>
                  <div>
                    <div className="font-medium text-apple-text">{s.display_name || s.username}</div>
                    <div className="text-xs text-apple-secondary">{s.username} · {s.essay_count} 篇作文</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {s.ability?.essay_count > 0 ? (
                    <Link to={`/teacher/student/${s.id}/ability`}
                          className="flex items-center gap-2 bg-blue-50 rounded-xl px-3 py-1.5 hover:bg-blue-100 transition-all">
                      <Target className="w-3.5 h-3.5 text-apple-accent" />
                      <span className="text-sm font-semibold text-apple-accent">{s.ability.overall_score}</span>
                      <span className="text-xs text-apple-secondary">/45</span>
                      <ChevronRight className="w-3.5 h-3.5 text-apple-disabled" />
                    </Link>
                  ) : (
                    <span className="text-xs text-apple-secondary">暂无能力数据</span>
                  )}
                </div>
              </div>
              {s.ability?.essay_count > 0 && (
                <div className="mt-3 pt-3 border-t border-apple-divider">
                  <div className="grid grid-cols-4 gap-4 text-center">
                    {[
                      { label: '立意', value: s.ability.abilities?.thesis, color: '#FF3B30' },
                      { label: '内容', value: s.ability.abilities?.content, color: '#007AFF' },
                      { label: '语言', value: s.ability.abilities?.language, color: '#34C759' },
                      { label: '结构', value: s.ability.abilities?.structure, color: '#FF9500' },
                      { label: '文面', value: s.ability.abilities?.penmanship, color: '#AF52DE' },
                    ].map(({ label, value, color }) => (
                      <div key={label}>
                        <div className="text-xs text-apple-secondary mb-1">{label}</div>
                        <div className="text-sm font-semibold" style={{ color }}>{value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
