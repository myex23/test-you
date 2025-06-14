import os
import sys
import random
import logging
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import ffmpeg

# === CONFIGURATION ===
NUM_VIDEOS = 5  # Number of videos to generate
VIDEO_DURATION = 10  # seconds per video
RESOLUTION = (1080, 1920)  # Vertical video resolution

# Directories
QUOTES_FILE = "quotes.txt"
ASSET_VIDEO_DIR = Path("assets/videos")
ASSET_MUSIC_DIR = Path("assets/music")
OUTPUT_DIR = Path("output")
OVERLAY_DIR = Path("temp_overlays")

# Text settings for overlay
FONT_SIZE = 80
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust this path if needed.
WRAP_WIDTH = 28  # Maximum characters per line

# === LOGGING SETUP ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def ensure_directories():
    for directory in [ASSET_VIDEO_DIR, ASSET_MUSIC_DIR, OUTPUT_DIR, OVERLAY_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def load_quotes(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logging.error(f"Error loading quotes: {e}")
        sys.exit(1)

def select_random_video() -> Path:
    videos = list(ASSET_VIDEO_DIR.glob("*.mp4"))
    if not videos:
        logging.error(f"No video files found in {ASSET_VIDEO_DIR}")
        sys.exit(1)
    return random.choice(videos)

def select_random_music() -> Path:
    musics = list(ASSET_MUSIC_DIR.glob("*.mp4"))
    if not musics:
        logging.error(f"No music files found in {ASSET_MUSIC_DIR}")
        sys.exit(1)
    return random.choice(musics)

def create_text_overlay(quote: str, overlay_path: Path, video_size=RESOLUTION):
    """
    Create a PNG image with a black translucent rectangle and white text.
    The text is word-wrapped and centered.
    """
    img = Image.new("RGBA", video_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Wrap text into multiple lines
    wrapped_text = "\n".join(textwrap.wrap(quote, width=WRAP_WIDTH))

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception as e:
        logging.error(f"Error loading font: {e}")
        font = ImageFont.load_default()

    # Calculate text size
    lines = wrapped_text.split("\n")
    text_width = 0
    text_height = 0
    line_sizes = []
    for line in lines:
        size = draw.textsize(line, font=font)
        line_sizes.append(size)
        text_width = max(text_width, size[0])
        text_height += size[1]
    spacing = FONT_SIZE // 3
    text_height += spacing * (len(lines) - 1)

    # Draw translucent black rectangle as background
    padding = 20
    box_width = text_width + padding * 2
    box_height = text_height + padding * 2
    box_x = (video_size[0] - box_width) // 2
    box_y = (video_size[1] - box_height) // 2
    draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], fill=(0, 0, 0, 180))

    # Draw the wrapped text onto the image
    current_y = box_y + padding
    for line in lines:
        line_width, line_height = draw.textsize(line, font=font)
        x = (video_size[0] - line_width) // 2
        draw.text((x, current_y), line, font=font, fill="white")
        current_y += line_height + spacing

    img.save(overlay_path, "PNG")

def generate_video(quote: str, output_path: Path, video_path: Path, music_path: Path) -> bool:
    """
    Generate a video by extracting a 10-second subclip from a background video,
    overlaying a text image with the quote, and merging a background audio track.
    """
    try:
        # Create text overlay image
        overlay_file = OVERLAY_DIR / "overlay.png"
        create_text_overlay(quote, overlay_file, video_size=RESOLUTION)
        
        # Determine random start time for the video clip if video is longer than duration.
        # For simplicity, we assume the video duration is large enough. More robust code
        # might read the video metadata to select a random start.
        start_time = 0
        
        # Build ffmpeg input streams using ffmpeg-python.
        video_in = ffmpeg.input(str(video_path), ss=start_time, t=VIDEO_DURATION)
        video_in = video_in.filter('scale', RESOLUTION[0], RESOLUTION[1])
        overlay_in = ffmpeg.input(str(overlay_file))
        audio_in = ffmpeg.input(str(music_path), ss=0, t=VIDEO_DURATION)
        
        # Overlay the text image on the video clip.
        # The overlay filter centers the overlay image.
        video_with_overlay = ffmpeg.overlay(video_in, overlay_in, x='(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')
        
        # Combine video and audio, ensuring the output is 10 seconds long.
        (
            ffmpeg
            .output(video_with_overlay, audio_in, str(output_path),
                    vcodec='libx264', acodec='aac', strict='experimental',
                    pix_fmt='yuv420p', shortest=None)
            .overwrite_output()
            .run(quiet=True)
        )
        
        # Clean up overlay file
        if overlay_file.exists():
            overlay_file.unlink()
    except Exception as e:
        logging.error(f"Failed to generate video for quote \"{quote[:50]}...\": {e}")
        return False
    return True

def main():
    ensure_directories()
    quotes = load_quotes(QUOTES_FILE)
    if not quotes:
        logging.error("No quotes found in quotes.txt")
        sys.exit(1)
    random.shuffle(quotes)
    
    num_generated = 0
    idx = 0
    while num_generated < NUM_VIDEOS and idx < len(quotes):
        quote = quotes[idx]
        video_file = select_random_video()
        music_file = select_random_music()
        output_file = OUTPUT_DIR / f"motivation_{num_generated + 1}.mp4"
        logging.info(f"Generating video {num_generated + 1} for quote: {quote[:50]}...")
        if generate_video(quote, output_file, video_file, music_file):
            logging.info(f"Video saved: {output_file}")
            num_generated += 1
        else:
            logging.error("Video generation failed for this quote; skipping.")
        idx += 1

if __name__ == "__main__":
    main()