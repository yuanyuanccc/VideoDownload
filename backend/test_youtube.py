import yt_dlp
ydl = yt_dlp.YoutubeDL({'quiet': True, 'nocheckcertificate': True})
try:
    info = ydl.extract_info('https://www.youtube.com/watch?v=33bZIOLX4do', download=False)
    print('Title:', info.get('title'))
    print('Formats:', len(info.get('formats', [])))
except Exception as e:
    print('Error:', str(e))