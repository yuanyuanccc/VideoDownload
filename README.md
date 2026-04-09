# Video Downloader

支持多平台的视频下载工具 + AI 智能分析功能

## 功能特性

### 视频下载
- 支持 YouTube、B站、抖音等主流平台
- 多种清晰度可选
- 直链返回，服务器不存储

### AI 智能分析
- AI 视频总结（DeepSeek）
- 字幕提取
- 思维导图生成
- AI 问答互动

## 快速开始

### 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 配置

在 `backend/.env` 中配置：

```bash
# DeepSeek API (用于AI功能)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# B站登录Cookie (可选，用于获取会员字幕)
BILIBILI_SESSDATA=your_sessdata
```

### 运行

```bash
# 后端
cd backend
python run.py

# 前端
cd frontend
npm run dev
```

## API 文档

### 视频解析
- `POST /api/parse` - 解析视频信息
- `POST /api/stream` - 获取视频直链
- `POST /api/download` - 下载视频

### AI 功能
- `POST /api/ai/subtitle` - 字幕提取
- `POST /api/ai/summary/stream` - AI总结(流式)
- `POST /api/ai/chat/stream` - AI问答(流式)
- `POST /api/ai/mindmap` - 思维导图

详细文档见 [docs/](docs/) 目录

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Tailwind |
| 后端 | FastAPI + Python |
| 核心 | yt-dlp (1800+网站支持) |
| AI | DeepSeek API |