import { useEffect, useState } from 'react'
import { Save, CheckCircle, Lock } from 'lucide-react'
import api from '../../api/client'

const PROVIDERS = [
  { value: 'zhipu', label: '智谱 GLM (推荐)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek API' },
  { value: 'claude', label: 'Claude API' },
  { value: 'ollama', label: 'Ollama (本地)' },
]

export default function Settings() {
  const [config, setConfig] = useState({
    provider: 'zhipu', model_name: 'glm-4-flash', api_key: '',
    routing_strategy: 'smart' as 'smart' | 'cloud' | 'local',
  })
  const [saved, setSaved] = useState(false)

  // 密码修改
  const [oldPw, setOldPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [pwMsg, setPwMsg] = useState('')

  useEffect(() => {
    api.get('/config/ai').then(({ data }) => {
      if (data) setConfig((c) => ({ ...c, ...data, api_key: '' }))
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    await api.put('/config/ai', config)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleChangePw = async () => {
    if (!oldPw || !newPw) { setPwMsg('请填写旧密码和新密码'); return }
    if (newPw.length < 4) { setPwMsg('新密码至少4位'); return }
    try {
      await api.put('/auth/password', { old_password: oldPw, new_password: newPw })
      setPwMsg('密码修改成功')
      setOldPw(''); setNewPw('')
    } catch (err: any) {
      setPwMsg(err.response?.data?.detail || '修改失败')
    }
  }

  const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">设置</h2>
        <p className="text-apple-secondary mt-1">AI 配置与安全</p>
      </div>

      {/* Password Change */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] p-6 space-y-4">
        <div className="flex items-center gap-2 mb-1">
          <Lock className="w-5 h-5 text-apple-accent" />
          <h3 className="font-semibold text-apple-text">修改密码</h3>
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">旧密码</label>
          <input type="password" value={oldPw} onChange={(e) => setOldPw(e.target.value)} className={inputClass} placeholder="请输入旧密码" />
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">新密码</label>
          <input type="password" value={newPw} onChange={(e) => setNewPw(e.target.value)} className={inputClass} placeholder="请输入新密码" />
        </div>
        {pwMsg && (
          <p className={`text-sm text-center rounded-xl py-2 ${pwMsg.includes('成功') ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'}`}>{pwMsg}</p>
        )}
        <button onClick={handleChangePw} className="w-full py-2.5 bg-apple-text text-white rounded-xl font-medium text-sm hover:bg-black/80 transition-all">
          修改密码
        </button>
      </div>

      {/* AI Config */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] p-6 space-y-4">
        <h3 className="font-semibold text-apple-text">AI 模型配置</h3>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">提供商</label>
          <select value={config.provider} onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                  className={inputClass}>
            {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
          <input type="text" value={config.model_name} onChange={(e) => setConfig({ ...config, model_name: e.target.value })}
                 className={inputClass} placeholder="如 claude-sonnet-4-6" />
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">API Key</label>
          <input type="password" value={config.api_key} onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                 className={inputClass} placeholder="填入 API Key" />
        </div>
        <button onClick={handleSave}
                className="w-full py-3 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
          {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? '已保存' : '保存配置'}
        </button>
      </div>
    </div>
  )
}
