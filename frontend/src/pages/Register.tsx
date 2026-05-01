import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus, BookOpen } from 'lucide-react'
import api from '../api/client'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '', password: '', display_name: '',
    real_name: '', school: '', teacher_cert: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!form.real_name || !form.school || !form.teacher_cert) {
      setError('请填写所有实名信息')
      return
    }
    setLoading(true)
    try {
      await api.post('/auth/register/teacher', form)
      alert('注册成功！请登录')
      navigate('/login')
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #F2F2F7 0%, #E8E8ED 50%, #D1D1D6 100%)' }}>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <BookOpen className="w-12 h-12 text-apple-accent mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-apple-text tracking-tight">教师实名注册</h1>
          <p className="text-apple-secondary mt-1 text-sm">注册后即可创建班级和管理学生</p>
        </div>
        <div className="backdrop-blur-2xl bg-white/70 rounded-[24px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_8px_24px_rgba(0,0,0,0.06)] p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-apple-text mb-1">用户名</label>
                <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                       className={inputClass} placeholder="登录用" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-apple-text mb-1">密码</label>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                       className={inputClass} placeholder="不少于6位" required />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-apple-text mb-1">显示名称</label>
                <input type="text" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                       className={inputClass} placeholder="如：李老师" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-apple-text mb-1">真实姓名 <span className="text-red-400">*</span></label>
                <input type="text" value={form.real_name} onChange={(e) => setForm({ ...form, real_name: e.target.value })}
                       className={inputClass} placeholder="身份证姓名" required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">任教学校 <span className="text-red-400">*</span></label>
              <input type="text" value={form.school} onChange={(e) => setForm({ ...form, school: e.target.value })}
                     className={inputClass} placeholder="如：深圳中学实验学校" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">教师资格证号 <span className="text-red-400">*</span></label>
              <input type="text" value={form.teacher_cert} onChange={(e) => setForm({ ...form, teacher_cert: e.target.value })}
                     className={inputClass} placeholder="用于实名验证" required />
            </div>
            {error && <p className="text-sm text-red-500 text-center bg-red-50 rounded-xl py-2">{error}</p>}
            <button type="submit" disabled={loading}
                    className="w-full py-3.5 bg-apple-accent text-white rounded-full font-medium hover:bg-blue-600 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
              <UserPlus className="w-4 h-4" />
              {loading ? '注册中...' : '实名注册'}
            </button>
          </form>
          <p className="text-center text-sm text-apple-secondary mt-5">
            已有账号？
            <button onClick={() => navigate('/login')} className="text-apple-accent hover:underline ml-1 font-medium">返回登录</button>
          </p>
        </div>
      </div>
    </div>
  )
}
