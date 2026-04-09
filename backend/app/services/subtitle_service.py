import yt_dlp
import json
import re
import os
import tempfile
import logging
import subprocess
from typing import List, Optional, Dict
from datetime import timedelta
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleItem:
    def __init__(self, start: str, end: str, text: str):
        self.start = start
        self.end = end
        self.text = text

    def dict(self):
        return {"start": self.start, "end": self.end, "text": self.text}


class SubtitleService:
    def __init__(self):
        self.settings = get_settings()
        self.base_opts = {
            'quiet': True,
            'no_warnings': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsubs': True,
            'subtitleslangs': ['zh-CN', 'en', 'en-US', 'zh'],
            'socket_timeout': 30,
            'nocheckcertificate': True,
        }
        self.ffmpeg_location = 'C:/Users/Yuanc/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin'
        self.whisper_model = None

    def _parse_srt_time(self, time_str: str) -> timedelta:
        """解析SRT时间格式 00:00:00,000"""
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=float(seconds)
            )
        return timedelta(0)

    def _format_time(self, td: timedelta) -> str:
        """格式化时间为 HH:MM:SS"""
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _get_whisper_model(self):
        """获取或加载Whisper模型"""
        if self.whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info("加载 Whisper tiny 模型...")
                self.whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            except Exception as e:
                logger.error(f"加载 Whisper 模型失败: {e}")
                return None
        return self.whisper_model

    def _transcribe_audio(self, audio_path: str) -> List[SubtitleItem]:
        """使用Whisper转录音频"""
        model = self._get_whisper_model()
        if not model:
            logger.warning("Whisper 模型不可用，跳过 ASR 转录")
            return []

        try:
            logger.info(f"开始 Whisper 转录: {audio_path}")
            segments, info = model.transcribe(audio_path, language="zh")
            
            subtitles = []
            for seg in segments:
                start = self._format_time(timedelta(seconds=seg.start))
                end = self._format_time(timedelta(seconds=seg.end))
                text = seg.text.strip()
                if text:
                    subtitles.append(SubtitleItem(start, end, text))
            
            logger.info(f"Whisper 转录完成，共 {len(subtitles)} 条字幕")
            return subtitles
        except Exception as e:
            logger.error(f"Whisper 转录失败: {e}")
            return []

    def _download_audio_for_asr(self, url: str, temp_dir: str) -> Optional[str]:
        """下载视频音频用于ASR"""
        if 'bilibili.com' in url:
            return self._download_audio_bilibili(url, temp_dir)
        else:
            return self._download_audio_ytdlp(url, temp_dir)

    def _get_bilibili_info(self, url: str) -> Optional[Dict]:
        """使用B站API获取视频信息（无需登录）"""
        try:
            import requests
            
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
                    
                    # 获取 tags
                    tags = []
                    aid = video_data.get('aid')
                    if aid:
                        tags_url = f"https://api.bilibili.com/x/tag/archive/tags?aid={aid}"
                        tags_resp = requests.get(tags_url, headers=headers, timeout=10)
                        if tags_resp.status_code == 200:
                            tags_data = tags_resp.json()
                            if tags_data.get('code') == 0:
                                tags = [t['tag_name'] for t in tags_data.get('data', [])]
                    
                    # 构建描述文本
                    owner = video_data.get('owner', {})
                    uploader = owner.get('name', '')
                    stat = video_data.get('stat', {})
                    views = stat.get('view', 0)
                    duration = video_data.get('duration', 0)
                    
                    desc_parts = [
                        f"标题：{video_data.get('title', '')}",
                        f"UP主：{uploader}",
                        f"播放量：{views}",
                        f"时长：{duration}秒",
                    ]
                    if tags:
                        desc_parts.append(f"标签：{', '.join(tags)}")
                    
                    desc = video_data.get('desc', '')
                    if desc and desc != '1':
                        desc_parts.append(f"简介：{desc}")
                    
                    fallback_text = '\n'.join(desc_parts)
                    
                    return {
                        'title': video_data.get('title', ''),
                        'fallback_text': fallback_text,
                    }
            
            return None
        except Exception as e:
            logger.error(f"B站API调用失败: {e}")
            return None

    def _download_audio_bilibili(self, url: str, temp_dir: str) -> Optional[str]:
        """使用B站API下载音频 - 由于B站限制，暂时无法下载"""
        logger.warning("B站音频下载暂不支持")
        return None

    def _download_audio_ytdlp(self, url: str, temp_dir: str) -> Optional[str]:
        """使用yt-dlp下载音频"""
        try:
            output_path = os.path.join(temp_dir, "audio")
            
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'ffmpeg_location': self.ffmpeg_location,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            audio_file = output_path + ".m4a"
            if not os.path.exists(audio_file):
                audio_file = output_path + ".mp3"
            
            if os.path.exists(audio_file):
                return audio_file
            
            for ext in ['.m4a', '.mp3', '.webm', '.wav']:
                for f in os.listdir(temp_dir):
                    if f.startswith("audio") and ext in f:
                        return os.path.join(temp_dir, f)
            
            return None
        except Exception as e:
            logger.error(f"下载音频失败: {e}")
            return None

    def _parse_srt(self, srt_content: str) -> List[SubtitleItem]:
        """解析SRT字幕内容"""
        subtitles = []
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                time_line = lines[1]
                time_match = re.search(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', time_line)
                if not time_match:
                    continue
                
                start_time = self._format_time(self._parse_srt_time(time_match.group(1)))
                end_time = self._format_time(self._parse_srt_time(time_match.group(2)))
                text = '\n'.join(lines[2:]).strip()
                
                if text:
                    subtitles.append(SubtitleItem(start_time, end_time, text))
            except Exception as e:
                logger.warning(f"Failed to parse subtitle block: {e}")
                continue
        
        return subtitles

    def _parse_vtt(self, vtt_content: str) -> List[SubtitleItem]:
        """解析VTT字幕内容"""
        subtitles = []
        lines = vtt_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if '-->' in line:
                try:
                    time_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})', line)
                    if time_match:
                        start_str = time_match.group(1)
                        end_str = time_match.group(2)
                        
                        if len(start_str.split(':')) == 2:
                            start_str = f"00:{start_str}"
                        if len(end_str.split(':')) == 2:
                            end_str = f"00:{end_str}"
                        
                        start_time = self._format_time(self._parse_srt_time(start_str))
                        end_time = self._format_time(self._parse_srt_time(end_str))
                        
                        i += 1
                        text_lines = []
                        while i < len(lines) and lines[i].strip():
                            text_lines.append(lines[i].strip())
                            i += 1
                        
                        text = '\n'.join(text_lines).strip()
                        if text:
                            subtitles.append(SubtitleItem(start_time, end_time, text))
                    else:
                        i += 1
                except Exception as e:
                    i += 1
            else:
                i += 1
        
        return subtitles

    def extract_subtitles(self, url: str) -> Dict:
        """提取视频字幕"""
        logger.info(f"Extracting subtitles for: {url}")
        
        temp_dir = tempfile.mkdtemp()
        
        video_title = ""
        video_description = ""
        
        # 对于B站，先尝试用API获取基本信息
        if 'bilibili.com' in url:
            bili_info = self._get_bilibili_info(url)
            if bili_info:
                video_title = bili_info.get('title', '')
                video_description = bili_info.get('fallback_text', '')
                logger.info(f"B站API获取标题: {video_title}")
        
        opts = {
            **self.base_opts,
            'outtmpl': os.path.join(temp_dir, 'subtitles'),
            'ffmpeg_location': self.ffmpeg_location,
        }
        
        if 'bilibili.com' in url and self.settings.bilibili_sessdata:
            opts['cookies'] = f"SESSDATA={self.settings.bilibili_sessdata}"
        
        subtitles_list = []
        has_auto_subs = False
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            logger.warning(f"yt-dlp 提取失败: {e}")
            info = None
        
        # 确保有视频标题
        if not video_title:
            if info and info.get('title'):
                video_title = info.get('title', '未知视频')
            else:
                video_title = "未知视频"
        
        video_description = video_description or (info.get('description', '') or '' if info else '')
        
        # 处理无字幕情况（无论info是否存在）
        def handle_no_subtitles():
            logger.warning("No real subtitles available, trying Whisper ASR...")
            
            audio_path = self._download_audio_for_asr(url, temp_dir)
            if audio_path and os.path.exists(audio_path):
                subtitles_list = self._transcribe_audio(audio_path)
                if subtitles_list:
                    return {
                        "success": True,
                        "subtitles": [s.dict() for s in subtitles_list[:500]],
                        "title": video_title,
                        "is_auto": True,
                        "lang": "zh",
                        "asr_used": True
                    }
            
            # ASR 失败时，使用视频描述作为备选
            if video_description:
                logger.info("使用视频描述作为备选内容")
                return {
                    "success": True,
                    "subtitles": [],
                    "title": video_title,
                    "is_auto": False,
                    "lang": "zh",
                    "fallback_text": video_description[:5000]
                }
            
            return {
                "success": False,
                "error": "无法提取字幕。B站视频需要登录才能获取字幕，或安装 faster-whisper 进行语音识别",
                "subtitles": [],
                "title": video_title
            }
        
        try:
            # 继续处理字幕提取（如果info存在）
            if info:
                
                logger.info(f"Video title: {video_title}")
                logger.info(f"Available fields: subtitles={bool(info.get('subtitles'))}, automatic_captions={bool(info.get('automatic_captions'))}")
                
                available_subs = info.get('subtitles', {}) or info.get('automatic_captions', {}) or {}
                
                logger.info(f"Available subtitles keys: {list(available_subs.keys())}")
                
                # 检查是否有真正的字幕（排除 danmaku 弹幕）
                real_subs = {k: v for k, v in available_subs.items() if k != 'danmaku'}
                
                if not real_subs:
                    return handle_no_subtitles()
                
                target_lang = None
                for lang in ['zh-CN', 'zh-Hans', 'zh', 'en', 'en-US']:
                    if lang in available_subs:
                        target_lang = lang
                        if 'automatic' in available_subs.get(lang, [{}])[0]:
                            has_auto_subs = True
                        break
                
                if not target_lang:
                    target_lang = list(available_subs.keys())[0]
                
                sub_info = available_subs.get(target_lang, [])
                if sub_info and isinstance(sub_info, list):
                    for fmt in sub_info:
                        if fmt.get('ext') in ['srt', 'vtt']:
                            try:
                                sub_url = fmt.get('url')
                                if sub_url:
                                    import requests
                                    resp = requests.get(sub_url, timeout=15)
                                    if resp.status_code == 200:
                                        content = resp.text
                                        
                                        if fmt.get('ext') == 'srt':
                                            subtitles_list = self._parse_srt(content)
                                        else:
                                            subtitles_list = self._parse_vtt(content)
                                        
                                        if subtitles_list:
                                            break
                            except Exception as e:
                                logger.warning(f"Failed to download subtitle: {e}")
                                continue
                
                if not subtitles_list:
                    return {
                        "success": False,
                        "error": "无法解析字幕内容",
                        "subtitles": [],
                        "title": video_title
                    }
                
                return {
                    "success": True,
                    "subtitles": [s.dict() for s in subtitles_list[:500]],
                    "title": video_title,
                    "is_auto": has_auto_subs,
                    "lang": target_lang
                }
            else:
                # info 为 None 时，也尝试处理
                return handle_no_subtitles()
                
        except Exception as e:
            logger.error(f"Subtitle extraction error: {e}")
            # 即使出错，也尝试用描述作为备选
            if video_description:
                return {
                    "success": True,
                    "subtitles": [],
                    "title": video_title,
                    "is_auto": False,
                    "lang": "zh",
                    "fallback_text": video_description[:5000]
                }
            return {"success": False, "error": str(e), "subtitles": []}
        finally:
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def get_subtitle_text(self, subtitles: List[Dict], max_length: int = 10000, fallback_text: str = "") -> str:
        """将字幕列表转为纯文本（用于AI处理）"""
        if fallback_text:
            return fallback_text[:max_length]
        
        texts = []
        current_length = 0
        
        for sub in subtitles:
            text = sub.get('text', '').strip()
            if text:
                texts.append(text)
                current_length += len(text)
                if current_length > max_length:
                    break
        
        return '\n'.join(texts)


subtitle_service = SubtitleService()