# Progress Log

## 2026-04-30 ~ 2026-05-01

### 设计 ✅
- 需求澄清 → FastAPI+React → Apple UI

### 后端 ✅
- 8 模型 + JWT + 作文 CRUD + 文件解析
- AI 批改 (GLM-4) + OCR (GLM-4V) + 能力分析
- xlsx 导入导出 + 密码修改

### 前端 ✅
- 学生端 8 页 + 教师端 7 页
- Apple 风格 UI + 作文原文展示

### AI 优化 ✅
- 五维度评分 (立意+内容+语言+结构+文面)
- 切题硬限制 (离题≤10, 偏题≤29)
- OCR 限流重试 + 模型降级
- 模型可配置 (OCR/评分独立)

### 部署 ✅
- GitHub Actions → GHCR → Sealos
- SSH Git push 永久修复
- APK v1.0 构建成功

## 测试
| Test | Status |
|------|--------|
| Health / Login | ✓ |
| Topics (10) | ✓ |
| Essay + GLM-4 grading | ✓ |
| Image + GLM-4V OCR | ✓ |
| Ability analysis | ✓ |
| xlsx import/export | ✓ |
| Frontend build | ✓ |
| Docker build | ✓ |
| APK build | ✓ |
| Sealos public | ✓ |
