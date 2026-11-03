import os
import random
import urllib.request
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

# --- 1. FREE AI TEXT GENERATION ---
def generate_meme_content():
    API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
    headers = {"Content-Type": "application/json"}
    prompt = "Write a single, brutally dark humor one-liner joke. Keep it under 15 words, punchy, and shocking. No intro text, just the joke."
    payload = {
        "inputs": f"<start_of_turn>user\n{prompt}<end_of_turn><start_of_turn>model",
        "parameters": {"max_new_tokens": 50, "temperature": 0.9}
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                raw_text = data[0].get("generated_text", "")
                joke = raw_text.split("<end_of_turn>")[-1].strip()
                if len(joke) > 5:
                    return joke
    except Exception:
        pass

    fallbacks = [
        "My grandfather has the heart of a lion... and a lifetime ban from the national zoo.",
        "Give a man a match, and he'll be warm for a few hours. Set a man on fire, and he'll be warm for the rest of his life.",
        "I was digging in our backyard the other day and found a chest full of gold coins. I was about to run inside to tell my wife, but then I remembered why I was digging in the backyard."
    ]
    return random.choice(fallbacks)

# --- 2. AUTO-FETCH REAL MUSIC ---
def fetch_background_music(output_audio_path="temp_music.mp3"):
    audio_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c4/Beethoven_Moonlight_1st_movement.ogg/Beethoven_Moonlight_1st_movement.ogg.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    ]
    try:
        urllib.request.urlretrieve(random.choice(audio_urls), output_audio_path)
    except Exception:
        pass
    return output_audio_path

# --- 3. VIDEO COMPILER ---
def create_meme_video(text, output_video_path="meme_output.mp4"):
    width, height = 1080, 1920
    bg_color = (random.randint(5, 20), random.randint(5, 20), random.randint(5, 20))
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    for _ in range(50):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(random.randint(0, 40),)*3)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    margin = 80
    max_width = width - (margin * 2)
    lines, current_line = [], ""
    for word in text.split():
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        # Fixed: bbox returns (left, top, right, bottom) tuple, use index 0 for left
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    total_height = len(lines) * 80
    y = (height - total_height) / 2
    for line in lines:
        bbox = font.getbbox(line)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += 80

    temp_img_path = "temp_meme.png"
    image.save(temp_img_path, "PNG")

    audio_path = fetch_background_music("temp_audio.mp3")
    image_clip = ImageClip(temp_img_path).set_duration(7.0)
    try:
        audio_clip = AudioFileClip(audio_path).subclip(0, 7.0)
        video_clip = image_clip.set_audio(audio_clip)
    except Exception:
        video_clip = image_clip

    video_clip.fps = 24
    video_clip.write_videofile(
        output_video_path, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None
    )
    
    for p in [temp_img_path, audio_path]:
        if os.path.exists(p):
            os.remove(p)
            
    return output_video_path

# --- 4. PLATFORM PUBLISHING HOOKS ---
def post_to_youtube_shorts(video_path, caption):
    print(f"Ready for Buffer/API upload: {video_path}")

if __name__ == "__main__":
    print(f"Starting execution at {datetime.now()}")
    for i in range(1, 3):
        meme_text = generate_meme_content()
        video_filename = f"meme_video_{i}.mp4"
        
        print(f"Generating Video #{i}: {meme_text}")
        create_meme_video(meme_text, video_filename)
