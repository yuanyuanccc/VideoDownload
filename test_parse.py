import sys
sys.path.insert(0, 'D:/ProjectCode/VideoDownload/backend')
from app.services.ytdlp_service import ytdlp_service

result = ytdlp_service.parse_video('https://www.bilibili.com/video/BV1uYAuzYEjX/')
print(result)