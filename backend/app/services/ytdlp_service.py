import yt_dlp
from typing import Optional, List
from pydantic import BaseModel
import logging
import requests
import re
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoFormat(BaseModel):
    format_id: str
    quality: str
    ext: str
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None


class VideoInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    description: Optional[str] = None
    uploader: Optional[str] = None
    formats: List[VideoFormat] = []
    url: Optional[str] = None


class YtDlpService:
    def __init__(self):
        self.base_opts = {
            'quiet': True,
            'no_warnings': False,
            'extract_flat': False,
            'socket_timeout': 30,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_color': True,
            'http_chunk_size': 10485760,
            'ffmpeg_location': 'C:/Users/Yuanc/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Cookie': 'ttwid=1%7C1234567890abcdef;',
        }

    def _is_douyin_url(self, url: str) -> bool:
        return 'douyin.com' in url.lower() or 'v.douyin.com' in url.lower()

    def _resolve_short_url(self, url: str) -> str:
        """解析抖音短链接"""
        if 'v.douyin.com' in url:
            try:
                resp = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
                return resp.url
            except:
                pass
        return url

    def _extract_aweme_id(self, url: str) -> Optional[str]:
        """从URL中提取视频ID"""
        patterns = [
            r'/video/(\d+)',
            r'modal_id=(\d+)',
            r'aweme_id=(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _parse_douyin_by_api(self, url: str) -> Optional[dict]:
        """通过抖音API解析"""
        resolved_url = self._resolve_short_url(url)
        aweme_id = self._extract_aweme_id(resolved_url)
        
        if not aweme_id:
            return None
        
        api_url = f'https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}'
        
        try:
            resp = requests.get(api_url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                aweme_detail = data.get('aweme_detail', {})
                if aweme_detail:
                    video_info = aweme_detail.get('video', {})
                    download_addr = video_info.get('download_addr', {})
                    play_addr = video_info.get('play_addr', {})
                    
                    video_url = play_addr.get('url_list', [''])[0] or download_addr.get('url_list', [''])[0]
                    
                    if video_url:
                        return {
                            'title': aweme_detail.get('desc', '抖音视频'),
                            'thumbnail': aweme_detail.get('video', {}).get('cover', {}).get('url_list', [''])[0],
                            'video_url': video_url,
                            'duration': aweme_detail.get('duration'),
                            'uploader': aweme_detail.get('author', {}).get('nickname'),
                        }
        except Exception as e:
            logger.warning(f"Douyin API parse failed: {e}")
        
        return None

    def _parse_bilibili_by_api(self, url: str) -> Optional[VideoInfo]:
        """通过B站API解析视频"""
        try:
            import re
            bv_id_match = re.search(r'BV[\w]+', url)
            if not bv_id_match:
                return None
            bv_id = bv_id_match.group()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.bilibili.com/',
            }
            
            api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0 and data.get('data'):
                    video_data = data['data']
                    
                    title = video_data.get('title', 'B站视频')
                    pic = video_data.get('pic', '')
                    duration = video_data.get('duration', 0)
                    owner = video_data.get('owner', {})
                    uploader = owner.get('name', '')
                    
                    # 修复缩略图URL
                    if pic:
                        if pic.startswith('//'):
                            pic = 'https:' + pic
                        elif not pic.startswith('http'):
                            pic = 'https://' + pic
                        thumbnail = self._download_thumbnail(pic)
                    else:
                        thumbnail = None
                    
                    return VideoInfo(
                        title=title[:100],
                        thumbnail=thumbnail,
                        duration=duration,
                        description=video_data.get('desc', ''),
                        uploader=uploader,
                        formats=[
                            VideoFormat(
                                format_id='bilibili_dash',
                                quality='1080P',
                                ext='mp4',
                                filesize_approx=None,
                                resolution='1920x1080'
                            ),
                            VideoFormat(
                                format_id='bilibili_dash_720',
                                quality='720P',
                                ext='mp4',
                                filesize_approx=None,
                                resolution='1280x720'
                            ),
                            VideoFormat(
                                format_id='bilibili_dash_480',
                                quality='480P',
                                ext='mp4',
                                filesize_approx=None,
                                resolution='854x480'
                            ),
                        ],
                        url=url,
                        _video_url=f"https://www.bilibili.com/video/{bv_id}/"
                    )
        except Exception as e:
            logger.error(f"B站API解析失败: {e}")
        
        return None

    def parse_video(self, url: str) -> VideoInfo:
        """解析视频信息"""
        logger.info(f"Parsing video: {url}")
        
        if self._is_douyin_url(url):
            try:
                result = self._parse_douyin_by_api(url)
                if result and result.get('video_url'):
                    return VideoInfo(
                        title=result.get('title', '抖音视频')[:100],
                        thumbnail=self._download_thumbnail(result.get('thumbnail')) if result.get('thumbnail') else None,
                        duration=result.get('duration') / 1000 if result.get('duration') else None,
                        description=None,
                        uploader=result.get('uploader'),
                        formats=[
                            VideoFormat(
                                format_id='douyin_hd',
                                quality='HD',
                                ext='mp4',
                                filesize_approx=None,
                                resolution='1080p'
                            )
                        ],
                        url=url,
                        _video_url=result.get('video_url'),
                    )
            except Exception as e:
                logger.warning(f"Douyin parse failed: {e}")
        
        # B站视频尝试使用API
        if 'bilibili.com' in url:
            bili_result = self._parse_bilibili_by_api(url)
            if bili_result:
                return bili_result
        
        opts = {**self.base_opts, 'dump_single_json': True}
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("无法获取视频信息")
                
                formats = []
                for f in info.get('formats', []):
                    if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                        formats.append(VideoFormat(
                            format_id=str(f.get('format_id', '')),
                            quality=f.get('format_note', '') or f.get('resolution', 'unknown'),
                            ext=f.get('ext', 'mp4'),
                            filesize=f.get('filesize'),
                            filesize_approx=f.get('filesize_approx'),
                            resolution=f.get('resolution'),
                            fps=f.get('fps'),
                        ))
                
                return VideoInfo(
                    title=info.get('title', 'Unknown'),
                    thumbnail=self._download_thumbnail(info.get('thumbnail')),
                    duration=info.get('duration'),
                    description=info.get('description', '')[:500] if info.get('description') else None,
                    uploader=info.get('uploader'),
                    formats=formats,
                    url=url,
                )
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            raise

    def _download_thumbnail(self, url: str) -> Optional[str]:
        """下载缩略图并转换为base64"""
        if not url or not url.startswith('http'):
            return url
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                import base64
                import mimetypes
                ext = mimetypes.guess_extension(url) or '.jpg'
                return f"data:image/{ext.strip('.')};base64,{base64.b64encode(response.content).decode()}"
        except Exception as e:
            logger.warning(f"Failed to download thumbnail: {e}")
        return url

    def get_stream_url(self, url: str, format_id: str) -> str:
        """获取视频直链"""
        if 'douyin' in format_id:
            info = self.parse_video(url)
            return getattr(info, '_video_url', '')
        
        # B站dash格式 - 使用yt-dlp获取真实下载链接
        if 'bilibili' in url and 'bilibili_dash' in format_id:
            quality_map = {
                'bilibili_dash': '1080',
                'bilibili_dash_720': '720',
                'bilibili_dash_480': '480',
            }
            quality = quality_map.get(format_id, '1080')
            
            opts = {
                **self.base_opts,
                'format': f'bestvideo[height<={quality}]+bestaudio/best',
                'allow_unplayable_formats': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info and info.get('formats'):
                        # 找最佳格式
                        best = info['formats'][-1]
                        for f in info['formats']:
                            if f.get('height') and f.get('height') <= int(quality):
                                if f.get('url'):
                                    best = f
                                    break
                        return best.get('url', '')
            except Exception as e:
                logger.error(f"B站直链获取失败: {e}")
        
        opts = {
            **self.base_opts,
            'format': format_id,
            'allow_unplayable_formats': True,
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('url', '')

    def download_video(self, url: str, format_id: str, output_path: str = './downloads') -> str:
        """下载视频（合并音视频）"""
        import os
        os.makedirs(output_path, exist_ok=True)
        
        if 'douyin' in format_id:
            info = self.parse_video(url)
            video_url = getattr(info, '_video_url', '')
            if video_url:
                safe_title = f"video_{int(os.times().system * 1000)}"
                output_file = os.path.join(output_path, f"{safe_title}.mp4")
                
                download_headers = {**self.headers}
                response = requests.get(video_url, headers=download_headers, timeout=180, stream=True)
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                return output_file
        
        # B站dash格式 - 使用特殊处理
        if 'bilibili' in url and 'bilibili_dash' in format_id:
            quality_map = {
                'bilibili_dash': '1080',
                'bilibili_dash_720': '720',
                'bilibili_dash_480': '480',
            }
            quality = quality_map.get(format_id, '1080')
            
            safe_title = f"video_{int(os.times().system * 1000)}"
            opts = {
                **self.base_opts,
                'format': f'bestvideo[height<={quality}]+bestaudio/best',
                'outtmpl': os.path.join(output_path, f'{safe_title}.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [self._progress_hook],
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if not filename.endswith('.mp4'):
                    for f in os.listdir(output_path):
                        if f.endswith('.mp4'):
                            filename = os.path.join(output_path, f)
                            break
                return filename
        
        safe_title = f"video_{int(os.times().system * 1000)}"
        
        opts = {
            **self.base_opts,
            'format': f'{format_id}+bestaudio',
            'outtmpl': os.path.join(output_path, f'{safe_title}.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [self._progress_hook],
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not filename.endswith('.mp4'):
                for f in os.listdir(output_path):
                    if f.endswith('.mp4'):
                        filename = os.path.join(output_path, f)
                        break
            return filename
    
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            logger.info(f"Downloading: {percent}")
    
    def download_video_sync(self, url: str, format_id: str, output_path: str = './downloads'):
        """同步下载视频，带超时控制"""
        import os
        import threading
        import time
        
        result = {'success': False, 'filename': None, 'error': None}
        os.makedirs(output_path, exist_ok=True)
        
        safe_title = f"video_{int(time.time() * 1000)}"
        
        # 抖音直接下载
        if 'douyin' in format_id:
            try:
                info = self.parse_video(url)
                video_url = getattr(info, '_video_url', '')
                if not video_url:
                    result['error'] = '无法获取视频链接'
                    return result
                
                output_file = os.path.join(output_path, f"{safe_title}.mp4")
                response = requests.get(video_url, headers=self.headers, timeout=180, stream=True)
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                result['success'] = True
                result['filename'] = output_file
                return result
            except Exception as e:
                result['error'] = str(e)
                return result
        
        # B站dash格式
        if 'bilibili' in url and 'bilibili_dash' in format_id:
            quality_map = {
                'bilibili_dash': '1080',
                'bilibili_dash_720': '720',
                'bilibili_dash_480': '480',
            }
            quality = quality_map.get(format_id, '1080')
            
            opts = {
                **self.base_opts,
                'format': f'bestvideo[height<={quality}]+bestaudio/best',
                'outtmpl': os.path.join(output_path, f'{safe_title}.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [self._progress_hook],
                'timeout': 300,
            }
        else:
            opts = {
                **self.base_opts,
                'format': f'{format_id}+bestaudio',
                'outtmpl': os.path.join(output_path, f'{safe_title}.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [self._progress_hook],
                'timeout': 300,
            }
        
        def download_thread():
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    if not filename.endswith('.mp4'):
                        for f in os.listdir(output_path):
                            if f.endswith('.mp4'):
                                filename = os.path.join(output_path, f)
                                break
                    result['success'] = True
                    result['filename'] = filename
            except Exception as e:
                logger.error(f"Download error: {e}")
                result['error'] = str(e)
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        thread.join(timeout=180)
        
        if thread.is_alive():
            result['error'] = '下载超时'
        
        return result


ytdlp_service = YtDlpService()