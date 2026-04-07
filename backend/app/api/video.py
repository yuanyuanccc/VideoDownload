from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.ytdlp_service import ytdlp_service
from app.services.douyin_service import douyin_downloader
import os
import urllib.parse

router = APIRouter()


class ParseRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    format_id: str


class StreamRequest(BaseModel):
    url: str
    format_id: str


def is_douyin_url(url: str) -> bool:
    return 'douyin.com' in url.lower()


@router.post("/parse")
async def parse_video(request: ParseRequest):
    """解析视频信息"""
    try:
        if is_douyin_url(request.url):
            video_info = douyin_downloader.get_video_info(request.url)
            if not video_info:
                raise HTTPException(status_code=400, detail="无法获取抖音视频信息")
            return {
                "code": 0,
                "message": "success",
                "data": video_info
            }
        else:
            video_info = ytdlp_service.parse_video(request.url)
            return {
                "code": 0,
                "message": "success",
                "data": video_info.model_dump()
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {str(e)}")


@router.post("/stream")
async def get_stream_url(request: StreamRequest):
    """获取视频直链"""
    try:
        stream_url = ''
        if is_douyin_url(request.url):
            stream_url = douyin_downloader.get_stream_url(request.url, request.format_id)
        else:
            stream_url = ytdlp_service.get_stream_url(request.url, request.format_id)
        
        if not stream_url:
            raise HTTPException(status_code=400, detail="无法获取直链")
        return {
            "code": 0,
            "message": "success",
            "data": {"stream_url": stream_url}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取直链失败: {str(e)}")


@router.post("/download")
async def download_video(request: DownloadRequest):
    """下载视频"""
    try:
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        
        if is_douyin_url(request.url):
            filename = douyin_downloader.download_video(request.url, request.format_id, temp_dir)
        else:
            result = ytdlp_service.download_video_sync(request.url, request.format_id, temp_dir)
            if not result['success']:
                raise HTTPException(status_code=400, detail=result.get('error', '下载失败'))
            filename = result['filename']
        
        def file_iterator():
            try:
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        yield chunk
            finally:
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                except:
                    pass
        
        base_name = os.path.basename(filename)
        encoded_name = urllib.parse.quote(base_name)
        
        return StreamingResponse(
            file_iterator(),
            media_type='video/mp4',
            headers={
                'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_name}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"下载失败: {str(e)}")