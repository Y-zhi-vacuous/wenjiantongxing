import { useEffect, useState } from 'react'
import { Save, CheckCircle, Lock, Zap } from 'lucide-react'
import api from '../../api/client'

export default function Settings() {
  const [ocrConfig, setOcrConfig] = useState({
    model_name: 'glm-4.1v-thinking-flash',
    api_key: '',
    base_url: '',
  })
  const [saved, setSaved] = useState(false)

  // 密码修改
  const [oldPw, setOldPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [pwMsg, setPwMsg] = useState('')

  useEffect(() => {
    api.get('/config/ocr').then(({ data }) => {
      if (data) setOcrConfig({ model_name: data.model_name || 'glm-4.1v-thinking-flash', api_key: '', base_url: data.base_url || '' })
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    await api.put('/config/ocr', ocrConfig)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleTestConnection = async () => {
    try {
      const { data } = await api.post('/config/ocr/test')
      alert(data.message || (data.success ? '连接正常' : '连接失败'))
    } catch (err: any) {
      alert(err.response?.data?.detail || '测试失败')
    }
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
        <p className="text-apple-secondary mt-1">OCR 配置与安全</p>
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

      {/* v2.0: OCR Config Only */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] p-6 space-y-4">
        <div className="flex items-center gap-2 mb-1">
          <Zap className="w-5 h-5 text-apple-accent" />
          <h3 className="font-semibold text-apple-text">OCR 手写识别配置</h3>
        </div>
        <p className="text-xs text-apple-secondary -mt-2">配置手写作文图片的文字识别模型</p>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">OCR 模型名称</label>
          <input type="text" value={ocrConfig.model_name}
                 onChange={(e) => setOcrConfig({ ...ocrConfig, model_name: e.target.value })}
                 className={inputClass} placeholder="默认：glm-4.1v-thinking-flash" />
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">OCR API Key</label>
          <input type="password" value={ocrConfig.api_key}
                 onChange={(e) => setOcrConfig({ ...ocrConfig, api_key: e.target.value })}
                 className={inputClass} placeholder="填入智谱 API Key" />
        </div>
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">自定义端点 (可选)</label>
          <input type="text" value={ocrConfig.base_url}
                 onChange={(e) => setOcrConfig({ ...ocrConfig, base_url: e.target.value })}
                 className={inputClass} placeholder="留空则使用默认智谱端点" />
        </div>
        <div className="flex gap-3">
          <button onClick={handleTestConnection}
                  className="flex-1 py-2.5 border border-apple-accent text-apple-accent rounded-xl font-medium text-sm hover:bg-blue-50 transition-all">
            测试连接
          </button>
          <button onClick={handleSave}
                  className="flex-1 py-2.5 bg-apple-accent text-white rounded-xl font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
            {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? '已保存' : '保存配置'}
          </button>
        </div>
      </div>
    </div>
  )
}
