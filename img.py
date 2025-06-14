import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import shutil
import random

# --- CONFIGURATION ---
SUPPORTED_EXTS = ('.webp', '.jpg', '.jpeg', '.png')
POSTS_DIR = os.path.join(os.path.dirname(__file__), '_posts')
IMAGES_DEST_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'images')

# Array of possible URLs to choose from
URLS = [
    "https://www.createporn.com/gifs?filter=hot",
    "https://www.createporn.com/post/search?filter=top6&style=all&search=indian",
    "https://pornx.co/search",
    "https://thepornator.com/en/aiporn/category/latest.html",
    "https://winoai.art/galleries/featured/",
    "https://xgroovy.com/photos/categories/ai/?sort=new",
    "https://xgroovy.com/photos/?sort=new"
    # Add more URLs as needed
]

# Array of all possible categories
ALL_CATEGORIES = [
    "Erotic AI content", "NSFW AI art", "Sensual cosplay", "Intimate storytelling", "Ethical porn",
    "Audio stimulation", "Erotic voice acting", "Fantasy kink", "POV erotica", "Immersive erotica",
    "Real couple content", "Inclusive desire", "Consent-based play", "Roleplay fantasies", "Digital dominatrix",
    "Sensual choreography", "Slow burn erotica", "Curvy bodies", "Body positivity", "Self-pleasure",
    "Tan lines & lingerie", "Alt aesthetic girls", "Tattooed beauties", "Pierced & proud", "Shibari art",
    "Femme domination", "Sapphic desires", "Bi-curious stories", "Soft domination", "Queer kinks",
    "Gothic romance", "Dark fantasy erotica", "Virtual intimacy", "3D erotic games", "Interactive NSFW",
    "BookTok after dark", "Erotic audiobooks", "Romantasy erotica", "Pleasure activism", "Mindful kink",
    "Gender-fluid lovers", "Softcore surrealism", "ASMR tingles", "Latex & lace", "Eco-erotica",
    "Alt romance", "Spiritual kink", "Non-binary beauty", "Nerdy seduction", "Vintage boudoir",
    "E-girl erotica", "Punk lovers", "Kinky fairytales", "Soft lighting seduction", "Sensual teasing",
    "Erotic gaze", "Curvy goddess", "Intimate moaning", "Flirty smirk", "Sultry voice",
    "Passionate kisses", "Slow undress", "Sensual touch", "Candlelit scenes", "Erotic close-up",
    "Bedroom eyes", "Deep intimacy", "Softcore vibes", "Erotic dance", "Whispers of pleasure",
    "Mirror play", "Hands-on body", "Romantic kink", "Barefoot beauty", "Midnight fantasy",
    "Pillow talk", "Erotic tension", "Wet lips", "Breath play", "Feather touch",
    "Skin worship", "Morning after", "Flushed cheeks", "Caressing curves", "Erotic photography",
    "Body worship", "Tasteful nudity", "Natural curves", "Eclectic erotica", "Moonlit passion",
    "Artistic nudes", "Shadow play", "Erotic oil massage", "Back arch", "Erotic silhouette",
    "Voyeur fantasy", "Intimate POV", "Sultry laughter", "Morning seduction", "Erotic focus",
    "Wet skin", "Lip biting", "Glowing skin", "Fantasy lover", "Close contact",
    "Dirty whispers", "Sensual selfie", "Erotic slow burn", "Nighttime romance", "Hands in hair",
    "Raw connection", "Erotic vulnerability", "Soft domination", "Deep gaze", "Whispered desires",
    "Naughty librarian", "Kinky dreams", "Roleplay seduction", "Soft bondage", "Eye contact kink",
    "Bare skin", "Hidden desires", "Erotic surprise", "Naughty expression", "Dreamy pleasure",
    "Hands behind back", "Erotic tension build", "Smudged makeup", "Lace and desire", "After dark play",
    "Story-driven erotica", "Subtle dominance", "Erotic hair pulling", "Soft spanking", "Satin sheets",
    "Pleasure mapping", "Artistic control", "Deep touch", "Erotic adventure", "Closeness kink",
    "Shadow kink", "Creative kink", "Lip gloss fantasy", "Intimate reveal", "Full-body chills",
    "Erotic curves", "Mutual desire", "Teasing look", "Flushed skin", "Morning passion",
    "Erotic tension tease", "Subtle kink", "Elegant fetish", "Lover's breath", "Erogenous zones","Erotic escapism", "AI girlfriend fantasy", "Sensual slow talk", "Neon-lit seduction", "Cinematic erotica",
    "Sensory play", "Erotic art direction", "Cyberpunk intimacy", "Delicate restraint", "Erotic transformation",
    "Mid-century kink", "Dirty mind games", "Vocal tease", "Lustful narration", "Erotic dreamscape",
    "Obedience kink", "Retro fantasy play", "Unspoken desires", "NSFW role reversal", "AI lover POV",
    "Intimate rituals", "Lingerie worship", "Delirious pleasure", "Erotic duality", "Midnight surrender",
    "Skin-to-skin fantasy", "Dirty inner voice", "Whipped cream play", "Erotic archetypes", "Intimate rebellion",
    "Heat of the moment", "Lustful close-up", "Softcore narrative", "Nude shadows", "Afterglow vibes",
    "Dominant softness", "Ethereal kink", "Immersive passion", "AI sensuality", "Erotic dream roleplay",
    "Digital erotica realm", "Emotion-driven NSFW", "Cosmic sensuality", "Erotic friction", "BDSM whisper",
    "Slow strip tease", "Virtual lover intimacy", "Fantasy surrender"
    "Slow strip tease", "Virtual lover intimacy", "Fantasy surrender",    "MILF fantasy",
    "Stepsister roleplay",
    "Anal play",
    "Threesome action",
    "Public sex",
    "Creampie",
    "Facial finish",
    "Deepthroat",
    "Spitroast",
    "Pov blowjob",
    "Rough sex",
    "Booty worship",
    "Bukkake",
    "Face fucking",
    "Twerking tease",
    "Glory hole",
    "Cuckold kink",
    "Gangbang fantasy",
    "Pegging play",
    "Footjob",
    "Butt plug play",
    "Gagging sounds",
    "Pussy eating",
    "Titty fuck",
    "Choking kink",
    "Hair pulling",
    "Ass worship",
    "Cumshot compilation",
    "Double penetration",
    "Squirting orgasm",    "Giantess fetish",
    "Vore fantasy",
    "Chastity play",
    "Wrestling domination",
    "Cheerleader roleplay",
    "Football-themed kink",
    "Tan line fetish",
    "Enema fetish",
    "Hog tying",
    "CPR fetish",
    "Lactation play",
    "Public flashing",
    "JOI (jerk off instructions)",
    "Sneaker fetish",
    "Thigh worship",
    "Face sitting",
    "Femdom wrestling",
    "Mask kink",
    "Hand over mouth play",
    "Babysitter scenario",    "Hentai",
    "Latina",
    "Asian",
    "Ebony",
    "Pinay",
    "Lesbian",
    "MILF",
    "Anal",
    "Tradwife",
    "Demure",
    "Mindful pleasure",
    "Modest MILF",
    "Real amateur",
    "Teacher fantasy",
    "Coworker crush",
    "Office affair",
    "Workplace fantasy",
    "Mormon wife",
    "Mormon missionary",
    "Mormon threesome",
    "Athlete",
    "Gymnastics",
    "Swimmer",
    "Volleyball",
    "Sex Olympics",
    "Nude Olympics",
    "Animation",
    "3D animation",
    "Anime",
    "Virtual reality",
    "VR porn",
    "Safe for work",
    "Mindful JOI",
    "Mindful sex",
    "Simple sex",
    "Authentic sex",
    "Respectful sex",
    "Ethical porn",
    "Modesty",
    "Hawk Tuah"
]

def ensure_dirs():
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DEST_DIR, exist_ok=True)

def download_images_selenium(url, folder, scroll_pause=2, max_scrolls=10):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()

    if not os.path.exists(folder):
        os.makedirs(folder)

    formats = ('jpg', 'jpeg', 'png', 'gif','webp')
    imgs = soup.find_all('img')
    downloaded = 0
    saved_files = []

    for img in imgs:
        img_url = img.get('src') or img.get('data-src')
        if not img_url:
            continue

        img_url = urljoin(url, img_url)
        img_format = os.path.splitext(urlparse(img_url).path)[1][1:].lower()

        if img_format in formats:
            try:
                img_data = requests.get(img_url, timeout=10).content
                img_name = os.path.basename(urlparse(img_url).path)
                save_path = os.path.join(folder, img_name)
                with open(save_path, 'wb') as f:
                    f.write(img_data)
                print(f"Downloaded: {img_url}")
                downloaded += 1
                saved_files.append(save_path)
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")

    print(f"\nTotal images downloaded: {downloaded}")
    return saved_files

def generate_tags(title, categories):
    words = title.lower().split()
    return list(set(words + categories))

def create_post(new_file_name, categories):
    ext = os.path.splitext(new_file_name)[1].lower()
    if ext not in SUPPORTED_EXTS:
        return False

    title = os.path.splitext(new_file_name)[0].replace('-', ' ').replace('_', ' ').title()
    slug = title.lower().replace(' ', '-')
    date = time.strftime('%Y-%m-%d')
    post_filename = f"{date}-{slug}.md"
    post_path = os.path.join(POSTS_DIR, post_filename)

    if os.path.exists(post_path):
        print(f"⚠️ Post already exists: {post_filename}, skipped.")
        return False

    tags = generate_tags(title, categories)
    post_content = f"""---
layout: post
title: "{title}"
image: "/assets/images/{new_file_name}"
categories: [{', '.join(categories)}]
tags: [{', '.join(tags)}]
---
"""

    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(post_content)
    print(f"✅ Created post: {post_filename}")
    return True

def main():
    ensure_dirs()
    # Randomly select a URL from the array
    for i in URLS:
        url = i
        folder = "downloaded_images"
        print(f"Selected URL: {url}")

        saved_files = download_images_selenium(url, folder)

        # Filter only supported images
        images = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTS]
        if not images:
            print("No supported images found after download.")
            return

        # For each image, create a post (one by one)
        for file in images:
            ext = os.path.splitext(file)[1]
            new_file_name = f"{int(time.time()*1000)}{ext}"
            src_path = os.path.join(folder, file)
            dest_path = os.path.join(IMAGES_DEST_DIR, new_file_name)

            # Randomly select 5 unique categories for this post
            categories = random.sample(ALL_CATEGORIES, 5)

            created = create_post(new_file_name, categories)
            if created:
                shutil.move(src_path, dest_path)
                print(f"➡️ Moved image to: {dest_path}")
            time.sleep(0.01)  # Ensure unique filenames

        print('🎉 Post creation completed.')

if __name__ == "__main__":
    main() 