# 方案设计文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              前端 (Vue 3 + Vite + Tailwind)              │
│         深色主题 + 卡片布局 + 平台选择 + 清晰度选项       │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP API
        ┌─────────────▼─────────────┐
        │     FastAPI 后端 (Python)  │
        │   /api/parse  解析视频信息  │
        │   /api/download 下载视频    │
        │   /api/stream 直链返回      │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ yt-dlp  │  │ 抖音专用 │  │ ffmpeg  │
   │(主流平台)│  │ 解析模块 │  │ (合并)  │
   └─────────┘  └─────────┘  └─────────┘
```

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | 现代化前端框架，快速开发 |
| 前端样式 | 内联样式 | 参考ai.codefather.cn深色主题 |
| 后端框架 | FastAPI | 高性能Python Web框架 |
| 核心依赖 | yt-dlp | 14w+ Star，支持1800+网站 |
| 视频处理 | ffmpeg | 合并音视频流 |
| 部署 | 轻量级 | 无数据库，直链返回 |

## 3. API设计

### 3.1 解析视频信息
```
POST /api/parse
Request: { "url": "https://..." }
Response: {
    "code": 0,
    "data": {
        "title": "视频标题",
        "thumbnail": "base64缩略图",
        "duration": 32.67,
        "uploader": "上传者",
        "url": "原始URL",
        "formats": [
            {"format_id": "30080", "quality": "1920x1080", "ext": "mp4"},
            ...
        ]
    }
}
```

### 3.2 下载视频
```
POST /api/download
Request: { "url": "...", "format_id": "30080" }
Response: 视频文件流 (Content-Type: video/mp4)
```

### 3.3 获取直链
```
POST /api/stream
Request: { "url": "...", "format_id": "30080" }
Response: { "stream_url": "https://..." }
```

## 4. 前端页面设计

### 4.1 风格参考
参考 https://ai.codefather.cn/painting 的UI风格：
- 深色主题（深蓝黑背景 #0f0f23）
- 卡片网格布局
- 青色强调色 (#00d4ff)
- 简洁扁平化按钮

### 4.2 页面结构
```
┌─────────────────────────────────────────┐
│  导航栏 (Logo + 导航链接 + 登录/注册)     │
├─────────────────────────────────────────┤
│  Hero区域: 标题 + URL输入框 + 解析按钮    │
├─────────────────────────────────────────┤
│  视频信息区: 缩略图 + 标题 + 清晰度选择   │
├─────────────────────────────────────────┤
│  支持的平台展示 (紧凑标签式)             │
├─────────────────────────────────────────┤
│  VIP推广区域 (三种套餐对比)              │
└─────────────────────────────────────────┘
```

## 5. 支持的平台

| 平台 | 解析状态 | 下载状态 | 说明 |
|------|----------|----------|------|
| YouTube | ✅ | ✅ | yt-dlp原生支持 |
| Bilibili | ✅ | ✅ | yt-dlp原生支持 |
| 抖音 | ✅ | ✅ | iesdouyin公开API（无需登录） |
| TikTok | ⚠️ | ⚠️ | 需要登录cookies |
| Twitter | ✅ | ✅ | yt-dlp支持 |
| Instagram | ✅ | ⚠️ | 部分内容需要登录 |

## 6. 抖音解析方案（已实现）

### 6.1 技术原理
基于公开API `iesdouyin.com` 实现，无需登录即可解析：
1. 短链接 `v.douyin.com/xxx` → 302重定向获取真实URL
2. 从URL提取 `video_id`
3. 调用 `https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/` 获取视频信息
4. 若API失败，备用方案：从分享页面提取 `window._ROUTER_DATA`
5. 替换 `playwm` → `play` 去除水印

### 6.2 开源参考
方案参考自 [rathodpratham-dev/douyin_video_downloader](https://github.com/rathodpratham-dev/douyin_video_downloader)（MIT协议）

### 6.3 支持的URL格式
- `https://v.douyin.com/xxx/` （短链接）
- `https://www.douyin.com/video/xxx` （视频页）
- 搜索结果页带modal_id参数的URL

## 6. 清晰度排序逻辑

```javascript
// 前端按分辨率从高到低排序
formats.sort((a, b) => {
  const getRes = (q) => {
    if (q.includes('1080')) return 1080
    if (q.includes('720')) return 720
    if (q.includes('480')) return 480
    if (q.includes('360')) return 360
    return 0
  }
  return getRes(b.quality) - getRes(a.quality)
})
```

## 7. 下载流程

1. 用户输入视频URL
2. 后端自动识别平台（抖音/其他）
3. 调用对应解析器获取视频信息
4. 前端展示视频信息和清晰度选项
5. 用户选择清晰度后点击下载
6. 后端调用yt-dlp下载并合并音视频
7. 流式返回给浏览器触发下载

## 8. 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| 阶段1 | FastAPI后端 + yt-dlp封装 | ✅ 完成 |
| 阶段2 | Vue3 + Vite + Tailwind 前端框架 | ✅ 完成 |
| 阶段3 | 前后端联调 + UI精雕 | ✅ 完成 |
| 阶段4 | 付费系统集成 | ⏳ 待开发 |
| 阶段5 | 抖音专用解析模块 | ✅ 完成 |
| 阶段6 | AI 视频智能功能 | ✅ 完成 |

## 9. 项目文件结构

```
VideoDownload/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── video.py      # 视频解析 API
│   │   │   └── ai.py         # AI 功能 API
│   │   ├── services/
│   │   │   ├── ytdlp_service.py    # yt-dlp封装
│   │   │   ├── douyin_service.py   # 抖音专用模块
│   │   │   ├── subtitle_service.py # 字幕提取服务
│   │   │   └── ai_service.py       # AI 服务
│   │   ├── config.py        # 配置管理
│   │   └── main.py          # FastAPI入口
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.vue
│   │   │   ├── HeroSection.vue
│   │   │   ├── VideoInfo.vue
│   │   │   ├── VideoSummary.vue  # AI 功能组件
│   │   │   ├── PlatformGrid.vue
│   │   │   └── VipBanner.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   └── vite.config.js
├── docs/
│   ├── requirements.md       # 需求分析
│   ├── design.md            # 方案设计
│   └── ai-features.md       # AI 功能文档
└── README.md
```

## 10. AI 视频智能功能

### 10.1 功能列表

| 功能 | 优先级 | 说明 |
|------|--------|------|
| AI 视频总结 | P0 | 流式生成结构化视频总结 (DeepSeek) |
| 字幕提取 | P0 | 提取视频字幕内容 (yt-dlp) |
| 思维导图 | P1 | 基于总结生成思维导图 |
| AI 问答 | P2 | 基于视频内容进行问答 |

### 10.2 技术特点

- **流式输出**: 使用 SSE (Server-Sent Events) 实现实时流式输出
- **API 安全**: API Key 存储在环境变量，不暴露在代码中
- **字幕依赖**: YouTube 有原生字幕，B站需要登录

### 10.3 AI API 端点

```
POST /api/ai/subtitle         # 字幕提取
POST /api/ai/summary/stream   # AI总结 (SSE流式)
POST /api/ai/chat/stream      # AI问答 (SSE流式)
POST /api/ai/mindmap          # 思维导图
```

### 10.4 配置

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## 11. 部署方案

- 服务器：Linux服务器
- 依赖：Python 3.8+, Node.js 16+, ffmpeg
- 进程管理：gunicorn (后端) + nginx (前端静态文件)