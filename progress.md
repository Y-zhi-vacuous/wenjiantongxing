# Progress Log

## 2026-05-01

### 部署相关
- ✅ GitHub Actions 自动构建 Docker 镜像成功
- ✅ GHCR 镜像仓库: `ghcr.io/y-zhi-vacuous/wenjiantongxing:latest`
- ✅ GHCR 包改为 Public (Sealos 可拉取)
- ✅ Sealos 应用创建 (Form 模式)
- 🔲 Sealos 503 调试中 (已修复: seed + Dockerfile，待推送)
- ✅ Capacitor Android 项目初始化

### 代码质量
- ✅ TypeScript 构建 0 错误
- ✅ 前端 build 通过
- ✅ 后端 API 全链路测试通过
- ✅ 智谱 GLM-4 真实 AI 批改验证通过

### 文档
- ✅ task_plan.md 更新
- ✅ findings.md 更新 (含部署调试记录)
- ✅ progress.md 更新
- 🔲 README.md 更新

## Test Results
| Test | Status |
|------|--------|
| Backend health | ✓ |
| Student login | ✓ |
| Teacher login + real name | ✓ |
| Essay create + AI grade + report | ✓ (Zhipu GLM-4) |
| Ability analysis + improvement plan | ✓ |
| Password change | ✓ |
| Teacher creates student | ✓ |
| xlsx template download + import + export | ✓ |
| Frontend build (0 errors) | ✓ |
| Docker image build (GitHub Actions) | ✓ |
| GHCR image pullable | ✓ |
