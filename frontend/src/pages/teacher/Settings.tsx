import { useEffect, useState } from 'react'
import { Save, CheckCircle, Wifi, Brain, Sparkles } from 'lucide-react'
import api from '../../api/client'

const PROVIDERS = [
  { value: 'zhipu', label: '智谱 GLM' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'claude', label: 'Claude' },
  { value: 'ollama', label: 'Ollama (本地)' },
  { value: 'vllm', label: 'vLLM (本地)' },
]

const isCloud = (p: string) => ['zhipu', 'openai', 'deepseek', 'claude'].includes(p)
const isLocal = (p: string) => ['ollama', 'vllm'].includes(p)
const inputClass = "w-full px-4 py-3 rounded-xl border border-apple-divider bg-[#F2F2F7] text-apple-text placeholder:text-apple-disabled focus:outline-none focus:ring-2 focus:ring-apple-accent/30 focus:border-apple-accent transition-all text-sm"

export default function TeacherSettings() {
  const [grading, setGrading] = useState({
    use_default: true, provider: 'zhipu', model_name: 'GLM-4-Flash-250414',
    api_key: '', base_url: '', local_url: '',
  })
  const [ability, setAbility] = useState({
    use_default: true, provider: '', model_name: '',
    api_key: '', base_url: '', local_url: '',
  })
  const [saved, setSaved] = useState(false)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    api.get('/config/grading').then(({ data }) => {
      if (data) {
        setGrading({
          use_default: data.grading_use_default !== false,
          provider: data.grading_provider || 'zhipu',
          model_name: data.grading_model_name || 'GLM-4-Flash-250414',
          api_key: '', base_url: data.grading_base_url || '', local_url: data.grading_local_url || '',
        })
        setAbility({
          use_default: data.ability_use_default !== false,
          provider: data.ability_provider || '',
          model_name: data.ability_model_name || '',
          api_key: '', base_url: data.ability_base_url || '', local_url: data.ability_local_url || '',
        })
      }
    }).catch(() => {})
  }, [])

  const handleSave = async () => {
    await api.put('/config/grading', {
      grading_use_default: grading.use_default,
      grading_provider: grading.provider,
      grading_model_name: grading.model_name,
      grading_api_key: grading.api_key,
      grading_base_url: grading.base_url || null,
      grading_local_url: grading.local_url || null,
      ability_use_default: ability.use_default,
      ability_provider: ability.provider || null,
      ability_model_name: ability.model_name || null,
      ability_api_key: ability.api_key,
      ability_base_url: ability.base_url || null,
      ability_local_url: ability.local_url || null,
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleTest = async () => {
    setTesting(true)
    try {
      await handleSaveQuick()
      const { data } = await api.post('/config/grading/test')
      alert((data.success ? 'OK ' : 'FAIL ') + data.message)
    } catch (err: any) {
      alert('FAIL ' + (err.response?.data?.detail || 'test error'))
    } finally { setTesting(false) }
  }

  const handleSaveQuick = () => api.put('/config/grading', {
    grading_use_default: grading.use_default,
    grading_provider: grading.provider,
    grading_model_name: grading.model_name,
    grading_api_key: grading.api_key,
    grading_base_url: grading.base_url || null,
    grading_local_url: grading.local_url || null,
    ability_use_default: ability.use_default,
    ability_provider: ability.provider || null,
    ability_model_name: ability.model_name || null,
    ability_api_key: ability.api_key,
    ability_base_url: ability.base_url || null,
    ability_local_url: ability.local_url || null,
  })

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-apple-text tracking-tight">AI 评分配置</h2>
        <p className="text-apple-secondary mt-1">勾选「默认」使用系统内置模型，取消勾选可自定义</p>
      </div>

      {/* Grading Model */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">评分模型</h3>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <span className="text-sm text-apple-secondary">默认</span>
            <input type="checkbox" checked={grading.use_default}
                   onChange={(e) => setGrading({ ...grading, use_default: e.target.checked })}
                   className="w-5 h-5 rounded-lg border-apple-divider text-apple-accent focus:ring-apple-accent" />
          </label>
        </div>

        {!grading.use_default && (
          <>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">提供商</label>
              <select value={grading.provider} onChange={(e) => setGrading({ ...grading, provider: e.target.value, base_url: '', local_url: '' })}
                      className={inputClass}>
                {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
            {isCloud(grading.provider) && (
              <>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
                  <input type="text" value={grading.model_name} onChange={(e) => setGrading({ ...grading, model_name: e.target.value })}
                         className={inputClass} placeholder="GLM-4-Flash-250414" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">API Key</label>
                  <input type="password" value={grading.api_key} onChange={(e) => setGrading({ ...grading, api_key: e.target.value })}
                         className={inputClass} placeholder="输入 API Key" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">自定义端点 (可选)</label>
                  <input type="text" value={grading.base_url} onChange={(e) => setGrading({ ...grading, base_url: e.target.value })}
                         className={inputClass} placeholder="留空用默认端点" />
                </div>
              </>
            )}
            {isLocal(grading.provider) && (
              <>
                <div className="p-3 rounded-xl bg-orange-50 text-orange-700 text-xs flex items-center gap-2">
                  <Wifi className="w-4 h-4" /> 确保服务已运行
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">本地端点</label>
                  <input type="text" value={grading.local_url} onChange={(e) => setGrading({ ...grading, local_url: e.target.value })}
                         className={inputClass} placeholder="http://localhost:11434" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
                  <input type="text" value={grading.model_name} onChange={(e) => setGrading({ ...grading, model_name: e.target.value })}
                         className={inputClass} placeholder="qwen3:latest" />
                </div>
              </>
            )}
          </>
        )}
        {grading.use_default && (
          <p className="text-xs text-apple-disabled">使用系统默认：智谱 GLM-4-Flash-250414</p>
        )}
      </div>

      {/* Ability Model */}
      <div className="bg-white/80 backdrop-blur-xl rounded-[20px] shadow-[0_1px_3px_rgba(0,0,0,0.04)] p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-apple-accent" />
            <h3 className="font-semibold text-apple-text">能力分析模型</h3>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <span className="text-sm text-apple-secondary">默认</span>
            <input type="checkbox" checked={ability.use_default}
                   onChange={(e) => setAbility({ ...ability, use_default: e.target.checked })}
                   className="w-5 h-5 rounded-lg border-apple-divider text-apple-accent focus:ring-apple-accent" />
          </label>
        </div>

        {!ability.use_default && (
          <>
            <div>
              <label className="block text-sm font-medium text-apple-text mb-1">提供商</label>
              <select value={ability.provider} onChange={(e) => setAbility({ ...ability, provider: e.target.value, base_url: '', local_url: '' })}
                      className={inputClass}>
                <option value="">同评分模型</option>
                {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
            {ability.provider && isCloud(ability.provider) && (
              <>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
                  <input type="text" value={ability.model_name} onChange={(e) => setAbility({ ...ability, model_name: e.target.value })}
                         className={inputClass} placeholder="GPT-4o-mini" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">API Key</label>
                  <input type="password" value={ability.api_key} onChange={(e) => setAbility({ ...ability, api_key: e.target.value })}
                         className={inputClass} placeholder="输入 API Key" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">自定义端点 (可选)</label>
                  <input type="text" value={ability.base_url} onChange={(e) => setAbility({ ...ability, base_url: e.target.value })}
                         className={inputClass} placeholder="留空用默认端点" />
                </div>
              </>
            )}
            {ability.provider && isLocal(ability.provider) && (
              <>
                <div className="p-3 rounded-xl bg-orange-50 text-orange-700 text-xs flex items-center gap-2">
                  <Wifi className="w-4 h-4" /> 确保服务已运行
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">本地端点</label>
                  <input type="text" value={ability.local_url} onChange={(e) => setAbility({ ...ability, local_url: e.target.value })}
                         className={inputClass} placeholder="http://localhost:11434" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-text mb-1">模型名称</label>
                  <input type="text" value={ability.model_name} onChange={(e) => setAbility({ ...ability, model_name: e.target.value })}
                         className={inputClass} placeholder="qwen3:latest" />
                </div>
              </>
            )}
            {!ability.provider && (
              <p className="text-xs text-apple-disabled">留空提供商则复用评分模型配置</p>
            )}
          </>
        )}
        {ability.use_default && (
          <p className="text-xs text-apple-disabled">使用系统默认：同评分模型（智谱 GLM-4-Flash-250414）</p>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={handleTest} disabled={testing}
                className="flex-1 py-3 border border-apple-accent text-apple-accent rounded-full font-medium text-sm hover:bg-blue-50 transition-all disabled:opacity-50">
          {testing ? '测试中...' : '测试连接'}
        </button>
        <button onClick={handleSave}
                className="flex-1 py-3 bg-apple-accent text-white rounded-full font-medium text-sm hover:bg-blue-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20">
          {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? '已保存' : '保存配置'}
        </button>
      </div>
    </div>
  )
}
