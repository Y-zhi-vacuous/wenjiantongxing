import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogIn, BookOpen } from 'lucide-react'
import api from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      const { data } = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate(data.user.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
    } catch {
      setError('用户名或密码错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #F2F2F7 0%, #E8E8ED 50%, #D1D1D6 100%)' }}>
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
      </div>
      <div className="w-full max-w-md relative">
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-[22px] flex items-center justify-center mx-auto mb-5 shadow-lg shadow-blue-500/20">
            <BookOpen className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-[28px] font-bold text-apple-text tracking-tight">文鉴同行</h1>
          <p className="text-apple-secondary mt-1.5 text-[15px]">深圳中考 AI 作文智能批改平台</p>
        </div>
        <div className="backdrop-blur-2xl bg-white/70 rounded-[24px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_8px_24px_rgba(0,0,0,0.06)] p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1.5">用户名</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                     className="w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"
                     placeholder="请输入用户名" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1.5">密码</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                     className="w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"
                     placeholder="请输入密码" required />
            </div>
            {error && <p className="text-sm text-red-500 text-center bg-red-50 rounded-xl py-2">{error}</p>}
            <button type="submit" disabled={loading}
                    className="w-full py-3.5 bg-apple-accent text-white rounded-full font-medium text-[15px] hover:bg-blue-600 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
              <LogIn className="w-4 h-4" />
              {loading ? '登录中...' : '登录'}
            </button>
          </form>
          <p className="text-center text-sm text-apple-secondary mt-6">
            教师账号？
            <button onClick={() => navigate('/register')} className="text-apple-accent hover:underline ml-1 font-medium">实名注册</button>
          </p>
          <p className="text-center text-xs text-apple-disabled mt-3">
            学生账号由教师统一创建和分发
          </p>
        </div>
      </div>
    </div>
  )
}
