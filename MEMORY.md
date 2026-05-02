# MEMORY.md — 文鉴同行 完整开发总结

## 项目概要

「文鉴同行」是一个 AI 驱动的深圳中考作文批改平台，通过智谱 GLM-4 大模型实现手写作文 OCR 识别、五维度智能评分、个性化能力画像分析。支持 Web 端和 Android APK，部署在 Sealos 免费 K8s 平台。

- **公网地址**：`https://wppyqjhwlqso.usw-1.sealos.app`
- **GitHub**：`https://github.com/Y-zhi-vacuous/wenjiantongxing`
- **开发周期**：2026-04-30 ~ 2026-05-02（约 30 小时）
- **代码规模**：~30 commits / ~8500 行 / 后端 35 文件 + 前端 22 文件 + 文档 8 文件

---

## 一、沟通协作模式

本项目采用 **AI 辅助全栈开发** 的协作模式。用户负责需求定义与决策，AI 负责设计、编码、部署、调试全流程。

### 协作流程

```
用户提出需求/问题
    │
    ▼
AI 分析 → 提出方案选项（含优缺点）
    │
    ▼
用户选择/确认
    │
    ▼
AI 实现 → 本地测试 → 推送 GitHub → Actions 构建 → Sealos 部署
    │
    ▼
用户验收 → 反馈问题 → AI 分析定位 → 修复 → 循环
```

### 关键沟通节点

| 阶段 | 沟通方式 | 典型案例 |
|------|----------|----------|
| 需求澄清 | AI 提问 → 用户单选/描述 | "目标用户是哪个学段？A/B/C/D" |
| 架构选型 | AI 提 2-3 方案+优劣 → 用户选 | FastAPI vs Jinja2 SSR vs Vue |
| 视觉设计 | AI 推送浏览器线框图 → 用户确认 | Apple Native 风格打样 |
| 问题反馈 | 用户描述现象 → AI 看日志定位 | "还是白屏"→ ErrorBoundary |
| 部署调试 | 用户操作 UI → AI 指导+AI 端测试 | Sealos 503 多轮排查 |
| 功能迭代 | 用户提改进方向 → AI 实现+验证 | "评分太多"→ 两步法 |
| 网络障碍 | 双方协同 push | "我这边连不上 → 你那边 push" |

### 协作中的关键教训

1. **网络不稳定是常态**：GitHub 在墙内 HTTPS 频繁被阻断，最终用 SSH Key 一劳永逸
2. **Web 部署工具链复杂**：Render/Sealos/Fly.io 均需浏览器授权，AI 无法独立完成
3. **AI 应主动暴露问题**：ErrorBoundary 让白屏变可诊断，日志输出让崩溃变可追踪
4. **本地先验证再部署**：每次改 Prompt 或模型参数，先在本地测试再推送

---

## 二、项目架构演进

### 2.1 初始架构（04-30 设计阶段）

```
浏览器 (React SPA)
    │ REST API
    ▼
FastAPI 后端
    ├── 认证 (JWT)
    ├── 作文 CRUD
    └── AI Agent (Mock)
    │
    ▼
PostgreSQL (Docker Compose)
```

最初设计使用 Docker Compose 本地开发，PostgreSQL 作为数据库。AI 批改用 Mock 模式独立开发调试。

### 2.2 开发阶段（05-01）

```
浏览器 (localhost:5173)
    │ Vite Proxy → localhost:8000
    ▼
FastAPI (SQLite 本地)
    ├── 8 张数据模型
    ├── 7 组 REST API
    ├── JWT 双模式 (Header + Query Param)
    └── AI Agent (Mock → GLM-4 真实 API)
```

**架构调整**：
- PostgreSQL → SQLite：因本地无 Docker，改为 aiosqlite 零配置方案
- 新增 JWT Query Param 模式：解决 `window.open()` 下载文件无法携带 Authorization Header 的问题
- 新增 StudentAbility 模型：在原有的 7 张表基础上增加第 8 张表，实现写作能力画像

### 2.3 生产部署架构（05-01 晚）

```
用户 (Web / Android APK)
    │ HTTPS
    ▼
Sealos K8s 免费集群
    ┌──────────────────────────┐
    │  Wenjiantongxing Pod     │
    │  ┌────────────────────┐  │
    │  │ FastAPI :8080      │  │
    │  │ ├── /api/* REST    │  │
    │  │ ├── /assets/* 静态  │  │
    │  │ └── /* SPA 兜底    │  │
    │  └────────────────────┘  │
    │  SQLite /app/data/       │
    └──────────────────────────┘
    │
    ▼
GitHub Actions → GHCR 镜像仓库
```

**部署架构特点**：
- **单容器方案**：FastAPI 同时提供 API + 静态文件 + SPA fallback，无需 Nginx
- **自包含数据库**：SQLite 零外部依赖，适合免费 K8s 环境
- **自动构建流水线**：git push → Actions → Docker → GHCR → Sealos Restart
- **SSH 通信**：Git 操作改用 SSH 协议，彻底解决 HTTPS 被 GFW 阻断的问题

### 2.4 AI 系统最终架构（05-02）

```
学生提交作文
    │
    ├── 文本模式 ──→ 直接送入评分流程
    │
    └── 图片模式 ──→ OCR 容错链 ──→ 纯文本 ──→ 评分流程
                         │
                         ├── >500KB → PIL 压缩
                         ├── glm-4.1v-thinking-flash (thinking:disabled)
                         ├── 失败 → 等 4s 重试
                         ├── 失败 → 等 8s 重试
                         ├── 失败 → 等 12s 重试
                         └── 失败 → glm-4v 降级

评分流程（两步法）
    │
    ├── [第1步] 独立切题检查 API
    │   ├── 专用 Prompt，仅判断切题/偏题/离题
    │   ├── temperature=0，max_tokens=10
    │   └── 输出：部分偏题
    │
    ├── [第2步] 主评分 API
    │   ├── Prompt 注入：【系统已判定：部分偏题】
    │   ├── 五维评分表 + 10条强制扣分规则
    │   └── 输出：JSON 评分报告
    │
    └── [第3步] 后端硬限制
        ├── 离题：立意≤2，总分≤10
        ├── 偏题：立意≤5，总分≤29
        ├── 各项 clamp 不超过满分
        └── 五项之和不等于总分时自动校正

能力分析流程
    │
    ├── 收集学生所有历史批改报告
    ├── GLM-4 综合分析（专用 Prompt）
    │   ├── 综合评估 (80-150字)
    │   ├── 优先改进方向
    │   ├── 五维分析 (assessment + action_items)
    │   └── 趋势分析
    └── AI 失败 → 关键词匹配降级
```

---

## 三、核心问题与解决过程

### 问题 1：前端白屏（无法诊断）

**现象**：部署后打开网页完全空白，无任何报错信息。

**排查过程**：
1. 检查 Vite 是否正常编译 → 正常
2. 检查 API 是否能访问 → 正常
3. 怀疑是 React 组件报错导致整个树崩溃

**解决方案**：在 App.tsx 中加入 ErrorBoundary 组件，捕获渲染异常并显示错误堆栈。从此白屏问题变为可诊断。

**教训**：SPA 应用必须有全局错误边界，否则一个组件崩溃会导致整个应用白屏。

### 问题 2：Git push 时通时断（持续整日）

**现象**：同一个网络环境下，有时能 push 成功，有时连接超时。严重影响部署效率。

**排查过程**：
1. 怀疑 GitHub 服务器不稳定 → 但网页始终能打开
2. 发现 HTTPS 443 端口的 git 协议被 QoS 限制
3. 尝试 HTTP/1.1 配置 → 无效

**解决方案**：生成 SSH Key 并添加到 GitHub，改用 `git@github.com:Y-zhi-vacuous/wenjiantongxing.git`。之后 push 从未失败。

**教训**：国内开发环境中，SSH 协议比 HTTPS 稳定得多，应在项目初期就配置好。

### 问题 3：OCR 完全不工作（6 轮迭代）

**第一轮**：本地 tesseract/pytesseract OCR → Windows 未安装，Sealos Docker 中也无法安装
**第二轮**：改用智谱 GLM-4V 视觉模型 → 返回 "asyncio.run() cannot be called from a running event loop"
**根因**：FastAPI 异步 handler 中调用了 `asyncio.run()`，而异步上下文已有运行中的事件循环
**解决**：改为 `await` 直接调用异步函数
**第三轮**：OCR 返回了文字，但只有 18 个字
**根因**：`glm-4.1v-thinking-flash` 是"思考模型"，大量 token 用于内部推理，实际输出极短
**解决**：在 API 请求中加入 `"thinking": {"type": "disabled"}` 关闭思考模式
**第四轮**：模型名 `glm-4v-flash` 不存在
**根因**：智谱的视觉模型命名是 `glm-4v`、`glm-4v-plus`，没有 `-flash` 后缀
**第五轮**：图片 6.3MB，base64 后 ~8.5MB，超过 API payload 限制
**解决**：PIL 自动压缩大图（尺寸缩半 + JPEG quality=60），压缩到 ~600KB
**第六轮**：`glm-4.1v-thinking-flash` 限流，"访问量过大请稍后再试"
**解决**：3 次重试（4/8/12 秒）+ 降级到 `glm-4v` 备用模型

**最终方案**：压缩 → glm-4.1v-thinking-flash(thinking:disabled) → 3 次重试 → glm-4v 降级

### 问题 4：AI 对离题作文打高分（5 轮迭代）

**第一轮**：简单四维 Prompt → AI 把"星光"作文判为主题切合，给 42/45
**根因**：Prompt 中没有题目信息，AI 只看作文本身的质量打分
**第二轮**：添加题目到 Prompt + 六类文评分表 → AI 仍然判"切题"给 34 分
**根因**：AI 看到"海边/沙滩/日落"关键词就认为切合"风景在变"，忽略了核心主题是"自我发现"
**第三轮**：添加 10 条强制扣分规则 + 审题作为评分第一步 → AI 仍然判"切题"
**根因**：单次 API 调用中，复杂的评分表干扰了审题判断，模型注意力被分散
**第四轮**：后端硬限制（clamp + topic_match 判定）→ 但 AI 仍然输出 `topic_match: "切题"`
**第五轮（突破）**：**两步法架构**
- 第一步：独立 API 调用，专用极简 Prompt（仅判断切题），temperature=0，max_tokens=10
- 第二步：将第一步结果强制注入评分 Prompt：`【系统已判定：部分偏题，请基于此判定进行评分】`
- 第三步：后端 clamp 硬上限（离题≤10/偏题≤29/各项不超满分）

**为什么两步法有效**：单次 API 调用中 LLM 的注意力被长 Prompt 中的评分表和各种规则稀释，审题判断不够专注。分离成两个独立调用后，第一步只有"对或错"一个任务，判断准确率大幅提升。

### 问题 5：能力分析千篇一律

**现象**：不同学生的能力画像建议几乎相同，无法体现个性化。

**根因**：`_generate_improvements()` 函数使用硬编码的模板建议（如"加强审题训练""每天记录素材"），仅通过分数阈值（<60/<80/≥80）选择不同的模板文案。

**第一轮修复**：从 AI 批改报告的真实建议中按关键词匹配维度 → 仍有混杂（如"审题"建议被匹配到"语言能力"维度）

**第二轮修复（AI 驱动）**：
- 收集学生所有历史批改报告中的分数和 AI 建议
- 调用 GLM-4 专用 Prompt，生成：
  - `overall_assessment`：80-150 字的综合能力评价
  - `priority`：当前最急需改进的 1-2 个方面
  - `dimensions`：每维度独立的 assessment + action_items
- AI 调用失败时回退关键词匹配降级方案

### 问题 6：Sealos 容器反复崩溃

**时间线**：
1. 首次部署 → 503 `no healthy upstream`
2. 排查日志 → SQLite `no such table: users`
3. 修复：seed.py 加 `Base.metadata.create_all`
4. 再次 503 → bcrypt 版本不兼容
5. 修复：锁定 `bcrypt==4.0.1`
6. 再次 503 → SQLite 数据库路径问题
7. 修复：Dockerfile 加 `mkdir -p /app/data`，使用绝对路径
8. 成功启动

**教训**：Docker 容器中的路径、权限、依赖版本问题在本地开发时往往不会暴露，必须逐层排查。

---

## 四、项目统计

| 类别 | 数量 |
|------|------|
| 总 Commits | ~30 |
| 总代码行 | ~8500 |
| 后端 Python 文件 | 35 |
| 前端 TS/TSX/CSS 文件 | 22 |
| 数据模型 | 8 张表 |
| API 路由组 | 7 组 |
| 学生端页面 | 8 |
| 教师端页面 | 7 |
| 题库（深圳中考真题） | 8 + 2 |
| AI 评分维度 | 5 (立意/内容/语言/结构/文面) |
| OCR 模型 | 2 (主/备) |
| 部署调试轮数 | 15+ |
| 文档文件 | 8 |
