from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from app.services.subtitle_service import subtitle_service
from app.services.ai_service import ai_service
from app.config import get_settings
import json

router = APIRouter()
settings = get_settings()


class SubtitleRequest(BaseModel):
    url: str


class SummaryRequest(BaseModel):
    url: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    url: str
    messages: List[ChatMessage]


class MindmapRequest(BaseModel):
    summary: str


@router.post("/subtitle")
async def get_subtitle(request: SubtitleRequest):
    """提取视频字幕"""
    try:
        result = subtitle_service.extract_subtitles(request.url)
        if not result.get("success"):
            return {
                "code": 1,
                "message": result.get("error", "提取字幕失败"),
                "data": None
            }
        return {
            "code": 0,
            "message": "success",
            "data": {
                "subtitles": result.get("subtitles", []),
                "title": result.get("title", ""),
                "is_auto": result.get("is_auto", False),
                "lang": result.get("lang", "unknown")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"提取字幕失败: {str(e)}")


@router.post("/summary/stream")
async def generate_summary_stream(request: SummaryRequest):
    """生成AI视频总结（SSE流式输出）"""
    try:
        sub_result = subtitle_service.extract_subtitles(request.url)
        if not sub_result.get("success"):
            return StreamingResponse(
                iter([f'data: {{"error": "{sub_result.get("error", "提取字幕失败")}"}}\n\n']),
                media_type="text/event-stream"
            )
        
        subtitle_text = subtitle_service.get_subtitle_text(
            sub_result.get("subtitles", []),
            settings.max_subtitle_length,
            sub_result.get("fallback_text", "")
        )
        
        if not subtitle_text:
            return StreamingResponse(
                iter([f'data: {{"error": "无法提取字幕文本"}}\n\n']),
                media_type="text/event-stream"
            )

        async def event_generator():
            for chunk in ai_service.generate_summary_stream(subtitle_text, sub_result.get("title", "")):
                yield chunk
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"生成总结失败: {str(e)}")


@router.post("/summary")
async def generate_summary(request: SummaryRequest):
    """生成AI视频总结（非流式）"""
    try:
        sub_result = subtitle_service.extract_subtitles(request.url)
        if not sub_result.get("success"):
            return {
                "code": 1,
                "message": sub_result.get("error", "提取字幕失败"),
                "data": None
            }
        
        subtitle_text = subtitle_service.get_subtitle_text(
            sub_result.get("subtitles", []),
            settings.max_subtitle_length
        )
        
        if not subtitle_text:
            return {
                "code": 1,
                "message": "无法提取字幕文本",
                "data": None
            }
        
        ai_result = ai_service.generate_summary(
            subtitle_text,
            sub_result.get("title", "")
        )
        
        if not ai_result.get("success"):
            return {
                "code": 1,
                "message": ai_result.get("error", "生成总结失败"),
                "data": None
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "summary": ai_result.get("content", ""),
                "title": sub_result.get("title", ""),
                "subtitle_count": len(sub_result.get("subtitles", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"生成总结失败: {str(e)}")


@router.post("/chat/stream")
async def chat_with_video_stream(request: ChatRequest):
    """AI问答（SSE流式输出）"""
    try:
        sub_result = subtitle_service.extract_subtitles(request.url)
        
        subtitle_text = subtitle_service.get_subtitle_text(
            sub_result.get("subtitles", []),
            8000,
            sub_result.get("fallback_text", "")  # 无字幕时使用视频描述
        )
        
        if not subtitle_text:
            return {
                "code": 1,
                "message": "无法获取视频内容",
                "data": None
            }
        
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        async def event_generator():
            for chunk in ai_service.chat_stream(subtitle_text, messages, sub_result.get("title", "")):
                yield chunk
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"问答失败: {str(e)}")


@router.post("/chat")
async def chat_with_video(request: ChatRequest):
    """AI问答（非流式）"""
    try:
        sub_result = subtitle_service.extract_subtitles(request.url)
        
        subtitle_text = subtitle_service.get_subtitle_text(
            sub_result.get("subtitles", []),
            8000,
            sub_result.get("fallback_text", "")  # 无字幕时使用视频描述
        )
        
        if not subtitle_text:
            return {
                "code": 1,
                "message": "无法获取视频内容",
                "data": None
            }
        
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        ai_result = ai_service.chat(
            subtitle_text,
            messages,
            sub_result.get("title", "")
        )
        
        if not ai_result.get("success"):
            return {
                "code": 1,
                "message": ai_result.get("error", "问答失败"),
                "data": None
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "reply": ai_result.get("content", ""),
                "title": sub_result.get("title", "")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"问答失败: {str(e)}")


@router.post("/mindmap")
async def generate_mindmap(request: MindmapRequest):
    """生成思维导图"""
    try:
        ai_result = ai_service.generate_mindmap(request.summary)
        
        if not ai_result.get("success"):
            return {
                "code": 1,
                "message": ai_result.get("error", "生成思维导图失败"),
                "data": None
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": ai_result.get("data")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"生成思维导图失败: {str(e)}")