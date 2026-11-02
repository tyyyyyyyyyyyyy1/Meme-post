import os
import random
import time
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION & SECRETS ---
# Secrets will be pulled from GitHub repository environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") # Or OAuth tokens depending on your setup
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

DARK_HUMOR_PROMPTS = [
    "Write a short, brutally dark humor setup and punchline about modern existential dread.",
    "Give me an absurd, pitch-black dark humor joke about medical anomalies or historical disasters.",
    "Create a micro-joke with a completely unexpected, morbidly funny twist.",
    "Write a dark humor one-liner about getting older and realizing nothing matters."
]

def generate_meme_content():
    """Generates unique dark humor text using Gemini API."""
    prompt = random.choice(DARK_HUMOR_PROMPTS)
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"{prompt} Keep it under 2 sentences. Make it punchy for a vertical video/image meme."}]}]
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
        except (KeyError, IndexError):
            pass
            
    return "When you realize adulthood is just choosing what to be tired about."

def create_meme_image(text, output_path="meme.png"):
    """Generates a vertical 1080x1920 image with randomized visual elements to avoid shadowbans."""
    width, height = 1080, 1920
    
    # Randomize background tone slightly (dark shades) to alter file hashes/metadata
    bg_color = (random.randint(10, 30), random.randint(10, 30), random.randint(10, 30))
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    # Anti-shadowban pixel tweak: Draw invisible or subtle randomized noise pixels
    for _ in range(50):
        rx, ry = random.randint(0, width), random.randint(0, height)
        draw.point((rx, ry), fill=(random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)))

    # Text rendering setup (Using default fallback or system font path if available)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    except IOError:
        font = ImageFont.load_default()

    # Word wrapping logic
    margin = 80
    max_width = width - (margin * 2)
    lines = []
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox.left
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Draw centered text
    total_height = len(lines) * 80
    y = (height - total_height) / 2
    
    for line in lines:
        bbox = font.getbbox(line)
        w = bbox[2] - bbox.left
        x = (width - w) / 2
        # Text shadow for readability
        draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += 80

    image.save(output_path, "PNG")
    print(f"Meme generated successfully at {output_path}")

def post_to_platforms(image_path, caption):
    """Placeholder function integrating your existing publishing pipelines."""
    print(f"Posting meme with caption: '{caption}'")
    # Insert your YouTube Shorts, Instagram Reels, and TikTok API dispatch code here
    # Ensure you add slight randomized tag variations or caption suffixes per post to avoid duplicate flagging.

if __name__ == "__main__":
    print(f"Starting daily meme generation batch at {datetime.now()}")
    for i in range(1, 3):
        print(f"Generating Meme #{i}...")
        meme_text = generate_meme_content()
        img_file = f"meme_{i}.png"
        create_meme_image(meme_text, img_file)
        
        # Unique AI caption generation
        caption = f"{meme_text} 💀 #darkhumor #relatable #meme"
        
        post_to_platforms(img_file, caption)
        
        # Stagger posts slightly
        if i == 1:
            time.sleep(5)
