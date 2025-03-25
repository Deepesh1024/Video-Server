import yt_dlp

def download_youtube_video(url, save_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/mp4', 
        'outtmpl': save_path,  
        'merge_output_format': 'mp4',
        'overwrites': True,
        'no_cache_dir': True,
        'verbose': True  
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])