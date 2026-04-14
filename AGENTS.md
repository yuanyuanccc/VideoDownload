# VideoGrab - AI Agent 能力文档

## 概述

VideoGrab 是一款专业的在线视频下载工具，支持从 YouTube、B站（哔哩哔哩）、抖音、TikTok、Twitter、Instagram、微博、快手、小红书等 **1800+** 视频平台解析和下载视频。

## 核心能力

### 1. 视频解析
- 输入：视频 URL
- 输出：视频标题、缩略图、时长、上传者、可用的清晰度列表
- API: `POST /api/parse`

### 2. 视频下载
- 输入：视频 URL + 选择的清晰度格式 ID
- 输出：视频文件流（直链返回，服务器不存储）
- API: `POST /api/download`

### 3. 直链获取
- 输入：视频 URL + 格式 ID
- 输出：可直接下载的视频 URL
- API: `POST /api/stream`

### 4. AI 智能分析
- **字幕提取**: 提取视频字幕内容
- **AI 总结**: 流式生成视频内容总结
- **思维导图**: 基于总结生成思维导图
- **AI 问答**: 基于视频内容进行问答互动
- API: 
  - `POST /api/ai/subtitle`
  - `POST /api/ai/summary/stream`
  - `POST /api/ai/mindmap`
  - `POST /api/ai/chat/stream`

## 支持的平台

| 平台 | 解析 | 下载 | 说明 |
|------|:----:|:----:|------|
| YouTube | ✅ | ✅ | 完全支持 |
| Bilibili | ✅ | ✅ | 完全支持 |
| 抖音 | ✅ | ✅ | 无需登录，自动去水印 |
| TikTok | ⚠️ | ⚠️ | 部分需要 cookies |
| Twitter/X | ✅ | ✅ | 完全支持 |
| Instagram | ⚠️ | ⚠️ | 部分内容需要登录 |
| 微博 | ✅ | ✅ | 完全支持 |
| 快手 | ✅ | ✅ | 完全支持 |
| 小红书 | ✅ | ✅ | 完全支持 |

## API 使用示例

### 视频解析

```bash
curl -X POST https://videograb.cc/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

响应：
```json
{
  "code": 0,
  "data": {
    "title": "视频标题",
    "thumbnail": "base64或URL",
    "duration": 123.45,
    "uploader": "上传者名称",
    "url": "原始视频URL",
    "formats": [
      {"format_id": "18", "quality": "360p", "ext": "mp4"},
      {"format_id": "22", "quality": "720p", "ext": "mp4"},
      {"format_id": "37", "quality": "1080p", "ext": "mp4"}
    ]
  }
}
```

### 视频下载

```bash
curl -X POST https://videograb.cc/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=example", "format_id": "22"}' \
  -o video.mp4
```

### AI 视频总结（流式）

```bash
curl -X POST https://videograb.cc/api/ai/summary/stream \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

## 定价方案

- **免费版**: ¥0/月，每日 3 次下载，高清画质
- **月付 VIP**: ¥29/月，无限制下载，4K 超清，AI 功能
- **年付 VIP**: ¥199/年，4K/8K 超清，完整 AI 功能

详细定价见: https://videograb.cc/pricing.md

## 集成说明

本工具适合以下场景集成：

1. **内容采集工具**: 自动下载视频素材
2. **社交媒体管理**: 批量获取视频内容
3. **AI 助手**: 为 AI 提供视频分析能力
4. **数据分析**: 批量采集视频数据进行研究

## 限制与注意事项

- 服务器不存储任何视频文件
- 直链返回，下载后立即释放内存
- 部分平台（如 TikTok、Instagram）可能需要登录 cookies
- 请遵守各平台的服务条款，合理使用

## 联系方式

- 官方网站: https://videograb.cc/
- 技术支持: 通过网站联系

---

最后更新: 2026-04-13