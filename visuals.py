import os
import requests
import re
import random
from dotenv import load_dotenv

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_relevant_images(script_text, topic): 
    os.makedirs("output/images", exist_ok=True)
    
    # 1. Clean and Split script into sentences
    sentences = re.split(r'(?<=[.!?]) +', script_text.strip())
    image_paths = []
    headers = {"Authorization": PEXELS_API_KEY}
    
    # 2. Duplicate Tracker: Keep track of IDs we've already used
    used_ids = set()

    print(f"🔍 Finding unique images for {len(sentences)} sentences...")

    for i, sentence in enumerate(sentences):
        # Extract meaningful keywords (longer words tend to be nouns)
        keywords = [w.strip(",.?!") for w in sentence.split() if len(w) > 4]
        query = f"{topic} {' '.join(keywords[:2])}" 
        
        # Try specific search first
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=15"
        
        try:
            response = requests.get(url, headers=headers).json()
            photos = response.get("photos", [])

            # 3. Smart Selection: Try to find a photo we haven't used yet
            selected_photo = None
            if photos:
                # Filter out photos we've already used in this session
                unused_photos = [p for p in photos if p['id'] not in used_ids]
                
                # If all 15 results were used (unlikely), just take any from the current set
                selected_photo = random.choice(unused_photos if unused_photos else photos)
            
            # 4. Fallback: If specific search failed, search the general topic
            else:
                print(f"⚠️ No match for '{query}'. Trying general topic...")
                fallback_url = f"https://api.pexels.com/v1/search?query={topic}&per_page=20"
                fallback_res = requests.get(fallback_url, headers=headers).json()
                f_photos = fallback_res.get("photos", [])
                
                if f_photos:
                    unused_f = [p for p in f_photos if p['id'] not in used_ids]
                    selected_photo = random.choice(unused_f if unused_f else f_photos)

            # 5. Download the Image
            if selected_photo:
                used_ids.add(selected_photo['id']) # Mark this ID as used
                img_url = selected_photo["src"]["large"] 
                
                img_data = requests.get(img_url).content
                path = f"output/images/img_{i}.jpg"
                
                with open(path, "wb") as f:
                    f.write(img_data)
                
                image_paths.append(path)
                print(f"✅ Image {i+1} saved: {query}")
            else:
                print(f"❌ Failed to find any image for sentence {i+1}")

        except Exception as e:
            print(f"❌ Error on sentence {i+1}: {e}")

    return image_paths