import os
import sys
import yt_dlp

def download_playlist_as_mp3(playlist_url, output_dir="downloads"):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(playlist_index)s - %(title)s.%(ext)s'),
        'extractaudio': True,
        'audioformat': 'mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'quiet': False,
        'progress_hooks': [download_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def download_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading: {d['filename']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_playlist.py <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    download_playlist_as_mp3(playlist_url)
