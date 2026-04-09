import requests
import json
import logging
from typing import List, Dict, Optional, Generator
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.settings = get_settings()
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = self.settings.deepseek_model

    def _get_headers(self) -> Dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.deepseek_api_key}"
        }

    def generate_summary_stream(self, subtitle_text: str, video_title: str = "") -> Generator[str, None, None]:
        """生成视频总结（流式输出）"""
        if not self.settings.deepseek_api_key:
            yield 'data: {"error": "未配置DeepSeek API Key"}\n\n'
            return

        system_prompt = """你是一个专业的视频内容分析师，擅长从字幕中提取关键信息并生成结构化总结。
请根据提供的字幕内容，生成视频总结，要求：
1. 视频主题（一句话概括）
2. 主要内容要点（3-5条）
3. 关键结论或信息
4. 适合观看的人群

请用中文回复，保持简洁清晰。"""

        user_prompt = f"""视频标题：{video_title}

字幕内容：
{subtitle_text}

请根据以上字幕内容生成结构化总结："""

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stream": True
                },
                timeout=60,
                stream=True
            )

            if response.status_code == 200:
                for chunk in response.iter_lines():
                    if chunk:
                        line = chunk.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            yield f"data: {data}\n\n"
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                yield f'data: {{"error": "API调用失败: {response.status_code}"}}\n\n'

        except Exception as e:
            logger.error(f"AI summary error: {e}")
            yield f'data: {{"error": "{str(e)}"}}\n\n'

    def chat_stream(self, subtitle_text: str, messages: List[Dict], video_title: str = "") -> Generator[str, None, None]:
        """AI问答（流式输出）"""
        if not self.settings.deepseek_api_key:
            yield 'data: {"error": "未配置DeepSeek API Key"}\n\n'
            return

        system_prompt = """你是一个专业的视频内容助手。用户会提供视频字幕内容和关于视频的问题，请根据字幕内容回答用户的问题。
如果问题与视频内容无关，请礼貌地说明你只能回答关于这个视频内容的问题。
请用中文回复，保持简洁准确。"""

        conversation = [{"role": "system", "content": system_prompt}]
        
        conversation.append({
            "role": "system", 
            "content": f"视频字幕内容：\n{subtitle_text[:8000]}\n\n（注意：如果字幕过长，仅显示前8000字符）"
        })
        
        for msg in messages[-5:]:
            conversation.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": conversation,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "stream": True
                },
                timeout=60,
                stream=True
            )

            if response.status_code == 200:
                for chunk in response.iter_lines():
                    if chunk:
                        line = chunk.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            yield f"data: {data}\n\n"
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                yield f'data: {{"error": "API调用失败: {response.status_code}"}}\n\n'

        except Exception as e:
            logger.error(f"AI chat error: {e}")
            yield f'data: {{"error": "{str(e)}"}}\n\n'

    def generate_summary(self, subtitle_text: str, video_title: str = "") -> Dict:
        """生成视频总结（非流式，兼容旧接口）"""
        if not self.settings.deepseek_api_key:
            return {"success": False, "error": "未配置DeepSeek API Key"}

        system_prompt = """你是一个专业的视频内容分析师，擅长从字幕中提取关键信息并生成结构化总结。
请根据提供的字幕内容，生成视频总结，要求：
1. 视频主题（一句话概括）
2. 主要内容要点（3-5条）
3. 关键结论或信息
4. 适合观看的人群

请用中文回复，保持简洁清晰。"""

        user_prompt = f"""视频标题：{video_title}

字幕内容：
{subtitle_text}

请根据以上字幕内容生成结构化总结："""

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {"success": True, "content": content}
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API调用失败: {response.status_code}"}

        except Exception as e:
            logger.error(f"AI summary error: {e}")
            return {"success": False, "error": str(e)}

    def chat(self, subtitle_text: str, messages: List[Dict], video_title: str = "") -> Dict:
        """AI问答（非流式，兼容旧接口）"""
        if not self.settings.deepseek_api_key:
            return {"success": False, "error": "未配置DeepSeek API Key"}

        system_prompt = """你是一个专业的视频内容助手。用户会提供视频字幕内容和关于视频的问题，请根据字幕内容回答用户的问题。
如果问题与视频内容无关，请礼貌地说明你只能回答关于这个视频内容的问题。
请用中文回复，保持简洁准确。"""

        conversation = [{"role": "system", "content": system_prompt}]
        
        conversation.append({
            "role": "system", 
            "content": f"视频字幕内容：\n{subtitle_text[:8000]}\n\n（注意：如果字幕过长，仅显示前8000字符）"
        })
        
        for msg in messages[-5:]:
            conversation.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": conversation,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {"success": True, "content": content}
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API调用失败: {response.status_code}"}

        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return {"success": False, "error": str(e)}

    def generate_mindmap(self, summary: str) -> Dict:
        """生成思维导图数据"""
        if not self.settings.deepseek_api_key:
            return {"success": False, "error": "未配置DeepSeek API Key"}

        system_prompt = """你是一个思维导图生成助手。请根据视频总结内容，生成思维导图JSON结构。
请返回纯JSON格式，不要任何其他文字。JSON格式：
{"root": "标题", "children": [{"text": "分支1", "children": [{"text": "子节点1"}]}]}"""

        try:
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"视频总结：\n{summary[:2000]}\n\n请生成思维导图JSON："}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 600
                },
                timeout=60
            )

            logger.info(f"Mindmap API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.info(f"Mindmap raw response: {content[:200]}")
                
                try:
                    mindmap_data = json.loads(content)
                    return {"success": True, "data": mindmap_data}
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        mindmap_data = json.loads(json_match.group())
                        logger.info(f"Mindmap parsed: {mindmap_data}")
                        return {"success": True, "data": mindmap_data}
                    return {"success": False, "error": f"无法解析JSON: {content[:100]}"}
            else:
                error_msg = f"API错误 {response.status_code}: {response.text[:200]}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"AI mindmap error: {e}")
            return {"success": False, "error": str(e)}


ai_service = AIService()