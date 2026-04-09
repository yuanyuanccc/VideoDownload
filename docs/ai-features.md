# AI 视频智能功能文档

## 1. 功能概述

AI 视频智能功能为用户提供视频内容的智能分析和交互能力，类似于 BibiGPT 和 NoteGPT。

### 1.1 功能列表

| 功能 | 优先级 | 说明 |
|------|--------|------|
| AI 视频总结 | P0 | 流式生成结构化Markdown总结 |
| 字幕提取 | P0 | 提取视频字幕内容 |
| 字幕下载 | P0 | 支持下载SRT格式字幕文件 |
| 思维导图 | P1 | 基于总结生成横向思维导图 |
| 思维导图下载 | P1 | 支持下载PNG图片和JSON |
| AI 问答 | P2 | 基于视频内容进行问答 |

### 1.2 展示特性

- **AI总结**: 支持Markdown富文本渲染(标题、加粗、斜体、列表、代码块)
- **思维导图**: 横向展开布局，支持手绘风格卡片
- **字幕**: 支持SRT标准格式下载

### 1.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                         │
│    VideoSummary.vue - 4标签页UI + SSE流式显示                │
└─────────────────────────┬───────────────────────────────────┘
                          │ SSE / HTTP
        ┌─────────────────▼─────────────────┐
        │         /api/ai (AI API)           │
        │  • /subtitle    字幕提取            │
        │  • /summary/stream  流式总结        │
        │  • /chat/stream  流式问答           │
        │  • /mindmap    思维导图            │
        └─────────────────┬─────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │           Services 层              │
        │  • subtitle_service.py  字幕提取    │
        │  • ai_service.py        AI处理     │
        └────────────────────────────────────┘
                          │
        ┌─────────────────▼─────────────────┐
        │           外部服务                 │
        │  • yt-dlp 字幕提取                 │
        │  • DeepSeek API (AI)              │
        └────────────────────────────────────┘
```

## 2. API 接口

### 2.1 字幕提取

**端点**: `POST /api/ai/subtitle`

**请求**:
```json
{
  "url": "https://youtube.com/watch?v=xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subtitles": [{"start": "00:00:00", "end": "00:00:05", "text": "内容"}],
    "title": "视频标题",
    "is_auto": false,
    "lang": "zh-CN"
  }
}
```

### 2.2 AI 总结 (流式)

**端点**: `POST /api/ai/summary/stream`

**响应**: SSE 流式输出

```javascript
// 前端处理示例
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  const lines = text.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      if (data.choices && data.choices[0].delta.content) {
        content += data.choices[0].delta.content;
      }
    }
  }
}
```

### 2.3 AI 问答 (流式)

**端点**: `POST /api/ai/chat/stream`

**请求**:
```json
{
  "url": "https://youtube.com/watch?v=xxx",
  "messages": [
    {"role": "user", "content": "这个视频讲了什么？"}
  ]
}
```

### 2.4 思维导图

**端点**: `POST /api/ai/mindmap`

**请求**:
```json
{
  "summary": "AI生成的视频总结内容"
}
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "root": "视频主题",
    "children": [
      {"text": "要点1", "children": [{"text": "子节点1"}]},
      {"text": "要点2", "children": []}
    ]
  }
}
```

## 3. 配置说明

### 3.1 环境变量

在 `.env` 文件中配置:

```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
```

### 3.2 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| deepseek_api_key | - | DeepSeek API Key (必填) |
| deepseek_model | deepseek-chat | 使用的模型 |
| max_subtitle_length | 10000 | 字幕最大字符数 |
| max_chat_context | 5 | 对话上下文轮数 |

## 4. 字幕提取说明

### 4.1 支持的平台

- YouTube ✅ (原生支持字幕)
- Bilibili ⚠️ (需要登录账号才能获取字幕)
- 其他平台 (依赖 yt-dlp 支持情况)

### 4.2 Bilibili 字幕限制

测试确认：B站视频的字幕 API (`/x/player/v2`) 返回 code -400，在未登录状态下无法获取字幕。

**解决方案**:
1. 登录获取 SESSDATA Cookie (推荐)
2. 使用 ASR 语音识别 (如 faster-whisper)
3. 使用第三方付费 ASR 服务

### 4.3 无字幕处理

当视频没有可用字幕时，API 返回:
```json
{
  "code": 1,
  "message": "No subtitles available. Bilibili videos require login to get subtitles."
}
```

## 5. 前端组件

### 5.1 VideoSummary.vue

4 标签页设计:
- **AI总结**: 点击生成按钮，流式显示总结内容
- **字幕**: 显示字幕列表，支持时间轴展示
- **思维导图**: 基于总结生成树形结构
- **问答**: 对话交互界面

### 5.2 事件流

```javascript
// SSE 连接建立
const response = await fetch('/api/ai/summary/stream', {
  method: 'POST',
  body: JSON.stringify({ url: videoUrl })
});

// 处理流数据
const reader = response.body.getReader();
// ... 解码和处理
```

## 6. 安全注意事项

### 6.1 API Key 保护

- ✅ API Key 存储在环境变量中
- ✅ 不硬编码在任何源代码中
- ✅ 不暴露在客户端

### 6.2 SSE 安全头

```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
}
```

## 7. 文件结构

```
backend/app/
├── api/
│   ├── video.py        # 视频解析 API
│   └── ai.py           # AI 功能 API
├── services/
│   ├── ytdlp_service.py    # 视频下载服务
│   ├── douyin_service.py   # 抖音解析服务
│   ├── subtitle_service.py # 字幕提取服务
│   └── ai_service.py      # AI 服务
├── config.py           # 配置管理
└── main.py            # FastAPI 入口

frontend/src/
├── components/
│   ├── VideoInfo.vue      # 视频信息组件
│   └── VideoSummary.vue   # AI 功能组件
└── App.vue
```

## 8. 依赖

### 8.1 Python 依赖

```
fastapi
uvicorn
yt-dlp
requests
pydantic
python-dotenv
```

### 8.2 前端依赖

```
vue
vite
```