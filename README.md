# VideoGrab 万能视频下载器

一个支持多平台的视频下载工具，还能用 AI 分析视频内容。

## 支持的平台

YouTube、B站、抖音、TikTok、Twitter、微博、快手、小红书等 1800+ 网站。

## 功能

- 视频下载，多种清晰度可选
- AI 自动总结视频内容
- 提取字幕
- 生成思维导图
- 跟视频对话，问任何问题

## 怎么用

### 1. 克隆项目

```bash
git clone https://github.com/yuanyuanccc/VideoDownload.git
cd VideoDownload
```

### 2. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 3. 配置

在 `backend/.env` 里加上你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-xxx
```

### 4. 启动

```bash
# 后端 (端口 8000)
cd backend
python run.py

# 前端 (端口 5173)
cd frontend
npm run dev
```

然后浏览器打开 http://localhost:5173

## 技术

- 前端：Vue 3 + Vite + Tailwind
- 后端：FastAPI + Python
- 视频处理：yt-dlp
- AI：DeepSeek

## 接口

| 接口 | 说明 |
|------|------|
| POST /api/parse | 解析视频 |
| POST /api/download | 下载视频 |
| POST /api/ai/summary | AI 总结 |
| POST /api/ai/subtitle | 提取字幕 |
| POST /api/ai/mindmap | 生成思维导图 |
| POST /api/ai/chat | 问答 |

##LICENSE

MIT