"""
抖音视频专用解析下载模块
基于公开API: iesdouyin.com (无需登录)
方案参考: rathodpratham-dev/douyin_video_downloader (MIT License)
"""
import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs

import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://www.douyin.com/",
}

API_URL = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class DouyinDownloader:
    def __init__(self, timeout: tuple = (10, 30), max_retries: int = 3, backoff_factor: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def is_douyin_url(self, url: str) -> bool:
        return 'douyin.com' in url.lower() or 'v.douyin.com' in url.lower()

    def _is_video_url(self, url: str) -> bool:
        """判断是否是有效的视频页面URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parse_qs(parsed.query)
        
        # 短链接 v.douyin.com/xxx 也是有效视频URL
        if 'v.douyin.com' in parsed.netloc:
            return True
        
        # 有效的视频路径
        if '/video/' in path:
            return True
        
        # 带modal_id参数的搜索页等也视为有效（有视频ID）
        if query.get('modal_id') or query.get('item_id') or query.get('aweme_id'):
            return True
            
        return False

    def _resolve_redirect_url(self, share_url: str) -> str:
        """解析短链接，获取真实URL"""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    share_url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    headers=DEFAULT_HEADERS,
                )
                response.raise_for_status()
                if response.url:
                    return response.url
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    raise Exception(f"链接解析失败: {e}")
                sleep_seconds = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning(f"链接解析失败 (尝试 {attempt}/{self.max_retries}): {e}, 重试 {sleep_seconds}s")
                time.sleep(sleep_seconds)
        return share_url

    def _extract_video_id(self, url: str) -> str:
        """从URL中提取视频ID"""
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        # 优先检查 modal_id 参数
        for key in ("modal_id", "item_ids", "group_id", "aweme_id", "item_id"):
            values = query.get(key)
            if values:
                match = re.search(r"(\d{8,24})", values[0])
                if match:
                    return match.group(1)

        for pattern in (r"/video/(\d{8,24})", r"/note/(\d{8,24})", r"/(\d{8,24})(?:/|$)"):
            match = re.search(pattern, parsed.path)
            if match:
                return match.group(1)

        fallback = re.search(r"(?<!\d)(\d{8,24})(?!\d)", url)
        if fallback:
            return fallback.group(1)

        raise Exception("无法从URL中提取视频ID")

    def _get_json_with_retry(self, url: str, params: dict = None) -> dict:
        """带重试的JSON请求"""
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise requests.HTTPError(f"Retryable HTTP {response.status_code}", response=response)
                response.raise_for_status()
                if not response.content:
                    raise ValueError("API响应为空")
                return response.json()
            except (requests.RequestException, ValueError) as e:
                last_error = e
                if attempt == self.max_retries:
                    break
                sleep_seconds = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning(f"API请求失败 (尝试 {attempt}/{self.max_retries}): {e}, 重试 {sleep_seconds}s")
                time.sleep(sleep_seconds)
        raise Exception(f"API请求失败: {last_error}")

    def _fetch_item_info_from_page(self, video_id: str, resolved_url: str) -> dict:
        """从分享页面解析视频信息（备用方案）"""
        if "iesdouyin.com" in urlparse(resolved_url).netloc:
            share_url = resolved_url
        else:
            share_url = f"https://www.iesdouyin.com/share/video/{video_id}/"

        # 使用移动端UA
        mobile_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.douyin.com/",
        }
        response = self.session.get(share_url, headers=mobile_headers, timeout=self.timeout)
        response.raise_for_status()
        html = response.text

        router_data = self._extract_router_data(html)
        if not router_data:
            raise Exception("无法从页面提取ROUTER_DATA")

        return self._extract_item_info_from_router(router_data)

    def _extract_router_data(self, html: str) -> dict:
        """从HTML中提取window._ROUTER_DATA"""
        marker = "window._ROUTER_DATA = "
        start = html.find(marker)
        if start < 0:
            return {}

        index = start + len(marker)
        while index < len(html) and html[index].isspace():
            index += 1

        if index >= len(html) or html[index] != "{":
            return {}

        depth = 0
        in_string = False
        escaped = False

        for cursor in range(index, len(html)):
            char = html[cursor]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            if depth == 0:
                payload = html[index:cursor + 1]
                try:
                    return json.loads(payload)
                except ValueError:
                    return {}
        return {}

    def _extract_item_info_from_router(self, router_data: dict) -> dict:
        """从ROUTER_DATA中提取item信息"""
        loader_data = router_data.get("loaderData", {})
        if not isinstance(loader_data, dict):
            return {}

        for key, node in loader_data.items():
            if not isinstance(node, dict):
                continue
            video_info_res = node.get("videoInfoRes", {})
            if not isinstance(video_info_res, dict):
                continue
            item_list = video_info_res.get("item_list", [])
            if item_list and isinstance(item_list[0], dict):
                return item_list[0]
        return {}

    def get_video_info(self, url: str) -> Optional[Dict]:
        """获取视频信息"""
        try:
            if not self.is_douyin_url(url):
                return None
            
            # 检查是否是有效的视频URL
            if not self._is_video_url(url):
                logger.warning(f"非视频页面URL，跳过: {url}")
                return None

            # 1. 解析短链接
            if 'v.douyin.com' in url:
                resolved_url = self._resolve_redirect_url(url)
            else:
                resolved_url = url

            logger.info(f"解析后的URL: {resolved_url}")

            # 2. 提取video_id - 优先从resolved_url提取，否则从原始url提取
            try:
                video_id = self._extract_video_id(resolved_url)
            except:
                video_id = self._extract_video_id(url)
            logger.info(f"视频ID: {video_id}")

            # 3. 调用公开API
            try:
                params = {"item_ids": video_id}
                data = self._get_json_with_retry(API_URL, params=params)

                if data.get("status_code") not in (0, None):
                    raise Exception(f"API返回错误: {data.get('status_code')}")

                item_list = data.get("item_list", [])
                if not item_list:
                    raise Exception("API未返回视频数据")
                item_info = item_list[0]
            except Exception as e:
                logger.warning(f"公开API失败: {e}, 尝试页面解析方案")
                item_info = self._fetch_item_info_from_page(video_id, resolved_url)
                if not item_info:
                    raise Exception("页面解析也失败")

            # 4. 提取视频信息
            title = item_info.get("desc") or f"抖音视频_{video_id}"
            video_data = item_info.get("video", {})
            cover_data = video_data.get("cover", {})

            # 获取无水印视频URL
            play_urls = video_data.get("play_addr", {}).get("url_list", [])
            if not play_urls:
                raise Exception("无法获取视频播放地址")

            # 替换 playwm 为 play 去除水印
            video_url = play_urls[0].replace("playwm", "play")

            # 获取封面
            cover_url = cover_data.get("url_list", [None])[0]
            if not cover_url:
                cover_url = video_data.get("origin_cover", {}).get("url_list", [None])[0]

            # 时长
            duration = (item_info.get("duration", 0) or 0) / 1000

            # 作者
            author = item_info.get("author", {})
            uploader = author.get("nickname", "")

            return {
                "title": title[:100] if title else "抖音视频",
                "thumbnail": cover_url,
                "duration": duration,
                "uploader": uploader,
                "url": url,
                "video_id": str(video_id),
                "formats": [
                    {
                        "format_id": "douyin_hd",
                        "quality": "HD",
                        "ext": "mp4",
                        "url": video_url,
                    }
                ],
                "_video_url": video_url,
            }

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return None

    def get_stream_url(self, url: str, format_id: str = None) -> Optional[str]:
        """获取视频直链"""
        video_info = self.get_video_info(url)
        if video_info and video_info.get("formats"):
            return video_info["formats"][0]["url"]
        return None

    def download_video(self, url: str, format_id: str = None, output_path: str = "./downloads") -> str:
        """下载视频"""
        import os
        os.makedirs(output_path, exist_ok=True)

        video_info = self.get_video_info(url)
        if not video_info or not video_info.get("formats"):
            raise Exception("无法获取视频信息")

        video_url = video_info["formats"][0]["url"]

        response = self.session.get(video_url, headers=DEFAULT_HEADERS, stream=True, timeout=180)
        response.raise_for_status()

        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff]', '', video_info["title"])[:50] or f"douyin_{video_info.get('video_id', 'video')}"
        filename = os.path.join(output_path, f"{safe_title}.mp4")

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return filename


douyin_downloader = DouyinDownloader()