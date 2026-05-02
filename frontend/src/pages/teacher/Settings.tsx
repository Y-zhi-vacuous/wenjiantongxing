import { useEffect, useState } from 'react'
import { Save, CheckCircle, Wifi } from 'lucide-react'
import api from '../../api/client'

const PROVIDERS = [
  { value: 'zhipu', label: '智谱 GLM (推荐)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek API' },
  { value: 'claude', label: 'Claude API' },
  { value: 'ollama', label: 'Ollama (本地部署)' },
  { value: 'vllm', label: 'vLLM (本地部署)' },
]

const isCloudProvider = (p: string) => ['zhipu', 'openai', 'deepseek', 'claude'].includes(p)
const isLocalProvider = (p: string) => ['ollama', 'vllm'].includes(p)

export default function TeacherSettings() {
  const [config, setConfig] = useState({
    provider: 'zhipu',
    grading_model_name: 'GLM-4-Flash-250414',
    ability_model_name: '',
    api_key: '',
    base_url: '',
    local_endpoint_url: '',
  })
  const [saved, setSaved] = useState(false)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    api.get('/config/grading').then(({ data }) => {
      if (data) setConfig({
        provider: data.provider || 'zhipu',
        grading_model_name: data.grading_model_name || 'GLM-4-Flash-250414',
        ability_model_name: data.ability_model_name || '',
        api_key: '',
        base_url: data.base_url || '',
        local_endpoint_url: data.local_endpoint_url || '',
      })
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    await api.put('/config/grading', config)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleTest = async () => {
    setTesting(true)
    try {
      const { data } = await api.post('/config/grading/test')
      alert(data.message || (data.success ? '连接正常' : '连接失败'))
    } catch (err: any) {
      alert(err.response?.data?.detail || '测试失败')
    } finally { setTesting(false) }
  }

  const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all"

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">AI 评分配置</h2>
        <p className="text-apple-secondary mt-1">配置评分模型与能力分析模型</p>
      </div>

      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.03)] p-6 space-y-4">
        {/* Provider */}
        <div>
          <label className="block text-sm font-medium text-apple-text mb-1">AI 提供商</label>
          <select value={config.provider}
                  onChange={(e) => setConfig({ ...config, provider: e.target.value, local_endpoint_url: '', base_url: '' })}
                  className={inputClass}>
            {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>

        {/* Cloud API Fields */}
        {isCloudProvider(config.provider) && (
          <>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">评分模型名称</label>
              <input type="text" value={config.grading_model_name}
                     onChange={(e) => setConfig({ ...config, grading_model_name: e.target.value })}
                     className={inputClass} placeholder="如 GLM-4-Flash-250414" />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">能力分析模型 (可选，默认同评分模型)</label>
              <input type="text" value={config.ability_model_name}
                     onChange={(e) => setConfig({ ...config, ability_model_name: e.target.value })}
                     className={inputClass} placeholder="默认同评分模型" />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">API Key</label>
              <input type="password" value={config.api_key}
                     onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                     className={inputClass} placeholder="填入 API Key" />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">自定义 API 端点 (可选)</label>
              <input type="text" value={config.base_url}
                     onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
                     className={inputClass} placeholder="留空使用默认端点" />
            </div>
          </>
        )}

        {/* Local LLM Fields */}
        {isLocalProvider(config.provider) && (
          <>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-orange-50 text-orange-700 text-xs">
              <Wifi className="w-4 h-4 flex-shrink-0" />
              <span>本地部署模式：请确保 {config.provider === 'ollama' ? 'Ollama' : 'vLLM'} 服务已在指定地址运行</span>
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">本地端点地址</label>
              <input type="text" value={config.local_endpoint_url}
                     onChange={(e) => setConfig({ ...config, local_endpoint_url: e.target.value })}
                     className={inputClass} placeholder={config.provider === 'ollama' ? 'http://localhost:11434' : 'http://localhost:8000'} />
            </div>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
              <input type="text" value={config.grading_model_name}
                     onChange={(e) => setConfig({ ...config, grading_model_name: e.target.value })}
                     className={inputClass} placeholder="如 qwen3:latest (Ollama) 或模型路径 (vLLM)" />
            </div>
          </>
        )}

        <div className="flex gap-3 pt-2">
          <button onClick={handleTest} disabled={testing}
                  className="flex-1 py-2.5 border border-apple-accent text-apple-accent rounded-xl font-medium text-sm hover:bg-blue-50 transition-all disabled:opacity-50">
            {testing ? '测试中...' : '测试连接'}
          </button>
          <button onClick={handleSave}
                  className="flex-1 py-2.5 bg-apple-accent text-white rounded-xl font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
            {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? '已保存' : '保存评分配置'}
          </button>
        </div>
      </div>
    </div>
  )
}
