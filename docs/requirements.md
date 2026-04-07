# 需求分析文档

## 1. 项目概述

### 1.1 背景
很多用户有下载保存视频到本地的需求，但存在以下痛点：
- 部分平台不支持直接下载功能
- 不支持批量下载
- 清晰度有限
- 操作繁琐

### 1.2 目标
开发一个万能视频下载网站，能够：
- 快速、随时随地从各个平台下载视频
- 支持手机端使用
- 提供付费增值服务

## 2. 用户画像

| 用户类型 | 特征 | 需求 |
|---------|------|------|
| 普通用户 | 偶尔下载视频 | 简单、快速、免费 |
| 重度用户 | 经常下载、批量需求 | 无限制、高清、批量 |
| 创作者 | 需要视频素材 | 高质量、多格式 |

## 3. 核心功能

### 3.1 基础功能
- 视频URL解析
- 视频信息展示（标题、时长、缩略图）
- 多清晰度选择
- 一键下载

### 3.2 付费功能
- 无限制下载次数
- 批量下载
- AI视频总结
- 字幕翻译

## 4. 技术约束
- 前端：Vue 3 + Vite + Tailwind CSS
- 后端：FastAPI + yt-dlp（Python）
- 无数据库，轻量级部署
- 直链返回，服务器不存储视频

## 5. 商业模式
- 免费版：每天3次下载（不限清晰度）
- 付费版：无限制 + 批量 + AI功能

## 6. 支持平台状态

| 平台 | 状态 | 说明 |
|------|------|------|
| YouTube | ✅ 正常 | yt-dlp直接支持 |
| Bilibili | ✅ 正常 | yt-dlp直接支持 |
| 抖音 | ✅ 正常 | iesdouyin公开API，无需登录 |
| TikTok | ⚠️ 部分 | 需要登录cookies |
| Twitter | ✅ 正常 | yt-dlp支持 |
| Instagram | ⚠️ 部分 | 部分内容需要登录 |

## 7. 抖音解析技术方案（已实现）

### 7.1 最终方案：iesdouyin公开API
采用公开API方案，无需登录cookies：
- API地址：`https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/`
- 备用方案：从分享页面提取 `window._ROUTER_DATA`
- 核心原理：替换URL中 `playwm` 为 `play` 去除水印

### 7.2 支持的URL格式
- 短链接：`https://v.douyin.com/xxx/`
- 视频页：`https://www.douyin.com/video/xxx`
- 带modal_id的搜索页URL

### 7.3 参考资源
- [rathodpratham-dev/douyin_video_downloader](https://github.com/rathodpratham-dev/douyin_video_downloader)（MIT协议）
- [Evil0ctal/Douyin_TikTok_Download_API](https://github.com/Evil0ctal/Douyin_TikTok_Download_API)