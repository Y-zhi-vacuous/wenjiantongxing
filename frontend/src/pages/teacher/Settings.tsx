import { useEffect, useState } from 'react'
import { Save, CheckCircle, Wifi, Brain, Sparkles } from 'lucide-react'
import api from '../../api/client'

const PROVIDERS = [
  { value: 'zhipu', label: '智谱 GLM (推荐)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek API' },
  { value: 'claude', label: 'Claude API' },
  { value: 'ollama', label: 'Ollama (本地部署)' },
  { value: 'vllm', label: 'vLLM (本地部署)' },
]

const isCloud = (p: string) => ['zhipu', 'openai', 'deepseek', 'claude'].includes(p)
const isLocal = (p: string) => ['ollama', 'vllm'].includes(p)

function ConfigSection({
  title, icon: Icon, provider, setProvider, modelName, setModelName,
  apiKey, setApiKey, baseUrl, setBaseUrl, localUrl, setLocalUrl,
  onTest, testing,
}: {
  title: string; icon: typeof Brain; provider: string; setProvider: (v: string) => void
  modelName: string; setModelName: (v: string) => void
  apiKey: string; setApiKey: (v: string) => void
  baseUrl: string; setBaseUrl: (v: string) => void
  localUrl: string; setLocalUrl: (v: string) => void
  onTest: () => void; testing: boolean
}) {
  const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all text-sm"

  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5 text-apple-accent" />
        <h3 className="font-semibold text-apple-text">{title}</h3>
      </div>
      <div>
        <label className="block text-sm font-medium text-apple-text mb-1">提供商</label>
        <select value={provider} onChange={(e) => { setProvider(e.target.value); setBaseUrl(''); setLocalUrl('') }}
                className={inputClass}>
          {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
        </select>
      </div>
      {isCloud(provider) && (
        <>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
            <input type="text" value={modelName} onChange={(e) => setModelName(e.target.value)}
                   className={inputClass} placeholder="如 GLM-4-Flash-250414" />
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">API Key</label>
            <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
                   className={inputClass} placeholder="填入 API Key" />
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">自定义端点 (可选)</label>
            <input type="text" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)}
                   className={inputClass} placeholder="留空使用默认端点" />
          </div>
        </>
      )}
      {isLocal(provider) && (
        <>
          <div className="p-3 rounded-xl bg-orange-50 text-orange-700 text-xs flex items-center gap-2">
            <Wifi className="w-4 h-4 flex-shrink-0" />
            确保 {provider === 'ollama' ? 'Ollama' : 'vLLM'} 服务已在指定地址运行
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">本地端点地址</label>
            <input type="text" value={localUrl} onChange={(e) => setLocalUrl(e.target.value)}
                   className={inputClass} placeholder={provider === 'ollama' ? 'http://localhost:11434' : 'http://localhost:8000'} />
          </div>
          <div>
            <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
            <input type="text" value={modelName} onChange={(e) => setModelName(e.target.value)}
                   className={inputClass} placeholder="如 qwen3:latest" />
          </div>
        </>
      )}
      <button onClick={onTest} disabled={testing}
              className="w-full py-2 border border-apple-accent text-apple-accent rounded-xl font-medium text-sm hover:bg-blue-50 transition-all disabled:opacity-50">
        {testing ? '测试中...' : '测试连接'}
      </button>
    </div>
  )
}

export default function TeacherSettings() {
  const [grading, setGrading] = useState({
    provider: 'zhipu', model_name: 'GLM-4-Flash-250414', api_key: '', base_url: '', local_url: '',
  })
  const [ability, setAbility] = useState({
    provider: '', model_name: '', api_key: '', base_url: '', local_url: '',
  })
  const [saved, setSaved] = useState(false)
  const [testingGrading, setTestingGrading] = useState(false)

  useEffect(() => {
    api.get('/config/grading').then(({ data }) => {
      if (data) {
        setGrading({
          provider: data.grading_provider || 'zhipu',
          model_name: data.grading_model_name || 'GLM-4-Flash-250414',
          api_key: '',
          base_url: data.grading_base_url || '',
          local_url: data.grading_local_url || '',
        })
        setAbility({
          provider: data.ability_provider || '',
          model_name: data.ability_model_name || '',
          api_key: '',
          base_url: data.ability_base_url || '',
          local_url: data.ability_local_url || '',
        })
      }
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    await api.put('/config/grading', {
      grading_provider: grading.provider,
      grading_model_name: grading.model_name,
      grading_api_key: grading.api_key,
      grading_base_url: grading.base_url || null,
      grading_local_url: grading.local_url || null,
      ability_provider: ability.provider || null,
      ability_model_name: ability.model_name || null,
      ability_api_key: ability.api_key,
      ability_base_url: ability.base_url || null,
      ability_local_url: ability.local_url || null,
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const testGrading = async () => {
    setTestingGrading(true)
    try {
      // Save first, then test
      await api.put('/config/grading', {
        grading_provider: grading.provider,
        grading_model_name: grading.model_name,
        grading_api_key: grading.api_key,
        grading_base_url: grading.base_url || null,
        grading_local_url: grading.local_url || null,
        ability_provider: ability.provider || null,
        ability_model_name: ability.model_name || null,
        ability_api_key: ability.api_key,
        ability_base_url: ability.base_url || null,
        ability_local_url: ability.local_url || null,
      })
      const { data } = await api.post('/config/grading/test')
      alert((data.success ? '✅ ' : '❌ ') + data.message)
    } catch (err: any) {
      alert('❌ ' + (err.response?.data?.detail || '测试失败'))
    } finally { setTestingGrading(false) }
  }

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">AI 评分配置</h2>
        <p className="text-apple-secondary mt-1">评分模型与能力分析模型可独立配置</p>
      </div>

      {/* Grading Model Config */}
      <ConfigSection
        title="评分模型" icon={Sparkles}
        provider={grading.provider} setProvider={(v) => setGrading({ ...grading, provider: v })}
        modelName={grading.model_name} setModelName={(v) => setGrading({ ...grading, model_name: v })}
        apiKey={grading.api_key} setApiKey={(v) => setGrading({ ...grading, api_key: v })}
        baseUrl={grading.base_url} setBaseUrl={(v) => setGrading({ ...grading, base_url: v })}
        localUrl={grading.local_url} setLocalUrl={(v) => setGrading({ ...grading, local_url: v })}
        onTest={testGrading} testing={testingGrading}
      />

      {/* Ability Model Config */}
      <ConfigSection
        title="能力分析模型（可选，默认使用评分模型）" icon={Brain}
        provider={ability.provider} setProvider={(v) => setAbility({ ...ability, provider: v })}
        modelName={ability.model_name} setModelName={(v) => setAbility({ ...ability, model_name: v })}
        apiKey={ability.api_key} setApiKey={(v) => setAbility({ ...ability, api_key: v })}
        baseUrl={ability.base_url} setBaseUrl={(v) => setAbility({ ...ability, base_url: v })}
        localUrl={ability.local_url} setLocalUrl={(v) => setAbility({ ...ability, local_url: v })}
        onTest={() => alert('能力分析模型暂不单独测试，将使用评分模型测试结果')}
        testing={false}
      />

      {/* Save All */}
      <button onClick={handleSave}
              className="w-full py-3 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
        {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
        {saved ? '已保存' : '保存全部配置'}
      </button>
    </div>
  )
}
