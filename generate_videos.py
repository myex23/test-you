import os
import sys
import random
import textwrap
import logging
from pathlib import Path
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import subprocess

# ========== CONFIGURATION ==========
NUM_VIDEOS = 5  # Number of videos to generate

QUOTES_FILE = "quotes.txt"
VIDEO_DIR = Path("assets/videos")
OUTPUT_DIR = Path("output")
TTS_AUDIO_DIR = Path("temp_audio")

VIDEO_DURATION = 10  # seconds
RESOLUTION = (1080, 1920)  # 9:16 vertical
FONT_SIZE = 72
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Change if needed
WRAP_WIDTH = 28

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def ensure_directories():
    for d in [VIDEO_DIR, OUTPUT_DIR, TTS_AUDIO_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def read_quotes():
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def select_random_video():
    videos = list(VIDEO_DIR.glob("*.mp4"))
    if not videos:
        logging.error(f"No videos found in {VIDEO_DIR}")
        sys.exit(1)
    return random.choice(videos)

def generate_tts_audio(quote, output_audio_path):
    tts = gTTS(quote, lang="en", slow=False)
    tts.save(output_audio_path)
    logging.info(f"TTS audio saved to {output_audio_path}")

def create_text_overlay(quote, overlay_path):
    # Prepare word-wrapped text
    wrapped = "\n".join(textwrap.wrap(quote, WRAP_WIDTH))
    img = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception as e:
        logging.warning(f"Could not load font at {FONT_PATH}, using default: {e}")
        font = ImageFont.load_default()
    # Calculate text size using multiline_textbbox
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=16)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    # Draw translucent black box behind text
    box_padding = 40
    box_w = text_w + box_padding * 2
    box_h = text_h + box_padding * 2
    box_x = (RESOLUTION[0] - box_w) // 2
    box_y = (RESOLUTION[1] - box_h) // 2
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 200))
    # Draw text centered
    text_x = (RESOLUTION[0] - text_w) // 2
    text_y = (RESOLUTION[1] - text_h) // 2
    draw.multiline_text((text_x, text_y), wrapped, font=font, fill="white", align="center", spacing=16)
    img.save(overlay_path, "PNG")
    logging.info(f"Overlay image saved to {overlay_path}")
    # Prepare word-wrapped text
    wrapped = "\n".join(textwrap.wrap(quote, WRAP_WIDTH))
    img = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception as e:
        logging.warning(f"Could not load font at {FONT_PATH}, using default: {e}")
        font = ImageFont.load_default()
    # Calculate text size
    text_w, text_h = draw.multiline_textsize(wrapped, font=font, spacing=16)
    # Draw translucent black box behind text
    box_padding = 40
    box_w = text_w + box_padding * 2
    box_h = text_h + box_padding * 2
    box_x = (RESOLUTION[0] - box_w) // 2
    box_y = (RESOLUTION[1] - box_h) // 2
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 200))
    # Draw text centered
    text_x = (RESOLUTION[0] - text_w) // 2
    text_y = (RESOLUTION[1] - text_h) // 2
    draw.multiline_text((text_x, text_y), wrapped, font=font, fill="white", align="center", spacing=16)
    img.save(overlay_path, "PNG")
    logging.info(f"Overlay image saved to {overlay_path}")

def run_ffmpeg(cmd):
    logging.info(f"Running ffmpeg: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error(f"ffmpeg failed: {e}")
        sys.exit(1)

def generate_video(quote, idx):
    video_path = select_random_video()
    tts_audio_path = TTS_AUDIO_DIR / f"tts_{idx}.mp3"
    overlay_path = TTS_AUDIO_DIR / f"overlay_{idx}.png"
    output_path = OUTPUT_DIR / f"motivation_{idx + 1}.mp4"
    # 1. Generate TTS
    generate_tts_audio(quote, str(tts_audio_path))
    # 2. Create overlay image
    create_text_overlay(quote, str(overlay_path))
    # 3. Extract a 10s vertical segment from source video, overlay text, mix with TTS audio
    # (a) Extract 10s, resize, mute (temp file)
    temp_clip = TTS_AUDIO_DIR / f"clip_{idx}.mp4"
    ffmpeg_extract = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-i", str(video_path),
        "-t", str(VIDEO_DURATION),
        "-vf", f"scale={RESOLUTION[0]}:{RESOLUTION[1]}:force_original_aspect_ratio=decrease,pad={RESOLUTION[0]}:{RESOLUTION[1]}:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(temp_clip)
    ]
    run_ffmpeg(ffmpeg_extract)
    # (b) Overlay text
    temp_overlay = TTS_AUDIO_DIR / f"with_text_{idx}.mp4"
    ffmpeg_overlay = [
        "ffmpeg", "-y",
        "-i", str(temp_clip),
        "-i", str(overlay_path),
        "-filter_complex", "overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2",
        "-c:a", "copy",
        "-c:v", "libx264",
        str(temp_overlay)
    ]
    run_ffmpeg(ffmpeg_overlay)
    # (c) Combine with TTS audio
    ffmpeg_audio = [
        "ffmpeg", "-y",
        "-i", str(temp_overlay),
        "-i", str(tts_audio_path),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        str(output_path)
    ]
    run_ffmpeg(ffmpeg_audio)
    # Cleanup temp files
    for f in [temp_clip, overlay_path, temp_overlay, tts_audio_path]:
        try:
            os.remove(f)
        except Exception:
            pass
    logging.info(f"Video saved: {output_path}")

def main():
    ensure_directories()
    quotes = read_quotes()
    random.shuffle(quotes)
    for idx, quote in enumerate(quotes[:NUM_VIDEOS]):
        logging.info(f"Generating video {idx + 1}/{NUM_VIDEOS}")
        generate_video(quote, idx)

if __name__ == "__main__":
    main()