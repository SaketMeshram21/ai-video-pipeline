import os
import traceback
from script_generator import generate_script
from voiceover import run_voice
from visuals import fetch_relevant_images
from video_maker import make_video
from moviepy import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, ColorClip

# --- Config ---
OUTPUT_DIR = "output"

def get_system_font_for_thumbnails():
    """
    Find an available system font by testing actual font files
    Returns full path to font file or None for default
    """
    import sys
    from PIL import ImageFont
    
    font_locations = []
    
    # Windows font paths
    if sys.platform == 'win32':
        font_locations = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/arialbd.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            'C:/Windows/Fonts/calibrib.ttf',
            'C:/Windows/Fonts/verdana.ttf',
            'C:/Windows/Fonts/verdanab.ttf',
            'C:/Windows/Fonts/tahoma.ttf',
            'C:/Windows/Fonts/tahomabd.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
            'C:/Windows/Fonts/segoeuib.ttf',
        ]
    
    # Test each font file
    for font_path in font_locations:
        if os.path.exists(font_path):
            try:
                # Try to load the font with PIL to verify it works
                test_font = ImageFont.truetype(font_path, 12)
                return font_path
            except Exception:
                continue
    
    # If no font found, return None
    return None

def generate_thumbnail_options(image_paths, topic):
    """Generate thumbnail options with proper error handling"""
    print("\n🖼️ Generating Ultimate Thumbnails...")
    
    if not image_paths:
        print("⚠️ No images available for thumbnails")
        return
    
    try:
        abs_out = os.path.abspath(OUTPUT_DIR)
        thumbnails_created = []
        
        # Find working font
        working_font = get_system_font_for_thumbnails()
        
        # --- Option 1: The "YouTuber" Style (Image + Shadow Box + Text) ---
        print("   ↳ Creating Style 1: Cinematic Title...")
        
        try:
            # Import the resize function
            from video_maker import resize_to_fill
            
            # Try to find a cinematic wallpaper style image first
            try:
                poster_search = fetch_relevant_images(f"best cinematic wallpaper {topic}", topic)
                bg_path = poster_search[0] if poster_search else None
            except Exception as e:
                print(f"   ⚠️ Could not fetch wallpaper image: {e}")
                bg_path = None
            
            # Fallback to first image if no wallpaper found
            if not bg_path and image_paths:
                bg_path = image_paths[0]
            
            if bg_path and os.path.exists(bg_path):
                bg_clip = resize_to_fill(ImageClip(bg_path), 1920, 1080)
                
                # Shadow Box (Semi-transparent black bar)
                shadow_box = ColorClip(
                    size=(1600, 300), 
                    color=(0, 0, 0)
                ).with_opacity(0.6).with_position('center')
                
                # Text Overlay with robust font handling
                txt_params = {
                    'text': topic.upper(),
                    'font_size': 90,  # Reduced from 110 to 90 for better fit
                    'color': 'white',
                    'stroke_color': 'black',
                    'stroke_width': 3,  # Reduced from 4 to 3
                    'method': 'caption',
                    'size': (1400, 250),  # Added height constraint to prevent cutoff
                    'text_align': 'center'
                }
                
                # Only add font if we have a valid path
                if working_font:
                    txt_params['font'] = working_font
                
                try:
                    txt = TextClip(**txt_params).with_position('center')
                    
                    # Composite
                    thumb = CompositeVideoClip([bg_clip, shadow_box, txt], size=(1920, 1080))
                    thumb_path = os.path.join(abs_out, "thumb_1_cinematic.png")
                    thumb.save_frame(thumb_path, t=0)
                    thumbnails_created.append(thumb_path)
                    print(f"   ✓ Cinematic thumbnail saved: thumb_1_cinematic.png")
                    
                    # Close clips to free memory
                    bg_clip.close()
                    txt.close()
                    thumb.close()
                    
                except Exception as txt_error:
                    # If font fails, try without font
                    if 'font' in txt_params:
                        print(f"   ⚠️ Font failed, trying default font for thumbnail")
                        del txt_params['font']
                        try:
                            txt = TextClip(**txt_params).with_position('center')
                            thumb = CompositeVideoClip([bg_clip, shadow_box, txt], size=(1920, 1080))
                            thumb_path = os.path.join(abs_out, "thumb_1_cinematic.png")
                            thumb.save_frame(thumb_path, t=0)
                            thumbnails_created.append(thumb_path)
                            print(f"   ✓ Cinematic thumbnail saved (default font): thumb_1_cinematic.png")
                            bg_clip.close()
                            txt.close()
                            thumb.close()
                        except Exception as e2:
                            print(f"   ⚠️ Could not create cinematic thumbnail: {e2}")
                            bg_clip.close()
                    else:
                        print(f"   ⚠️ Could not create cinematic thumbnail: {txt_error}")
                        bg_clip.close()
            else:
                print("   ⚠️ No valid background image for cinematic thumbnail")
                
        except Exception as e:
            print(f"   ⚠️ Could not create cinematic thumbnail: {e}")
            traceback.print_exc()

        # --- Option 2: The "Natural" (Clean Frame) ---
        print("   ↳ Creating Style 2: Clean Start...")
        
        try:
            if image_paths and os.path.exists(image_paths[0]):
                from video_maker import resize_to_fill
                clean_bg = resize_to_fill(ImageClip(image_paths[0]), 1920, 1080)
                thumb_path = os.path.join(abs_out, "thumb_2_clean.png")
                clean_bg.save_frame(thumb_path, t=0)
                thumbnails_created.append(thumb_path)
                print(f"   ✓ Clean thumbnail saved: thumb_2_clean.png")
                clean_bg.close()
            else:
                print("   ⚠️ No valid image for clean thumbnail")
        except Exception as e:
            print(f"   ⚠️ Could not create clean thumbnail: {e}")
            traceback.print_exc()

        if thumbnails_created:
            print(f"✅ {len(thumbnails_created)} thumbnail(s) saved successfully.")
        else:
            print("⚠️ No thumbnails were created")

    except Exception as e:
        print(f"❌ Thumbnail Generation Error: {e}")
        traceback.print_exc()

def validate_dependencies():
    """Check if all required modules are available"""
    missing = []
    
    try:
        import script_generator
    except ImportError:
        missing.append("script_generator.py")
    
    try:
        import voiceover
    except ImportError:
        missing.append("voiceover.py")
    
    try:
        import visuals
    except ImportError:
        missing.append("visuals.py")
    
    try:
        import whisper
    except ImportError:
        missing.append("whisper (install: pip install openai-whisper)")
    
    try:
        from moviepy import VideoFileClip
    except ImportError:
        missing.append("moviepy (install: pip install moviepy)")
    
    if missing:
        print("❌ Missing dependencies:")
        for m in missing:
            print(f"   - {m}")
        return False
    
    return True

def main():
    """Main execution function with comprehensive error handling"""
    print("=" * 50)
    print("🎬 AI Video Generator")
    print("=" * 50)
    
    # Validate dependencies
    if not validate_dependencies():
        print("\n❌ Please install missing dependencies and ensure all files are present.")
        return
    
    try:
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"✓ Output directory ready: {OUTPUT_DIR}")
        
        # Get topic from user
        topic = input("\n📝 Enter video topic: ").strip()
        
        if not topic:
            print("❌ Error: Topic cannot be empty")
            return
        
        print(f"\n🎯 Creating video about: '{topic}'")
        print("-" * 50)
        
        # Step 1: Generate Script
        print("\n1️⃣  Generating Script & Voice...")
        try:
            script = generate_script(topic)
            
            if not script or len(script.strip()) == 0:
                print("❌ Error: Script generation failed or returned empty content")
                return
            
            script_path = os.path.join(OUTPUT_DIR, "script.txt")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)
            
            print(f"✓ Script saved to: {script_path}")
            print(f"   Script length: {len(script)} characters")
            
        except Exception as e:
            print(f"❌ Script generation failed: {e}")
            traceback.print_exc()
            return
        
        # Step 2: Generate Voice
        try:
            run_voice(script)
            voice_path = os.path.join(OUTPUT_DIR, "voice.mp3")
            
            if not os.path.exists(voice_path):
                print(f"❌ Error: Voice file not created at {voice_path}")
                return
            
            print(f"✓ Voice generated: {voice_path}")
            
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            traceback.print_exc()
            return
        
        # Step 3: Fetch Images
        print("\n2️⃣  Fetching Visuals (Enhanced Relevance)...")
        try:
            # Enhanced search query for better quality
            enhanced_topic = f"cinematic high quality {topic}"
            images = fetch_relevant_images(script, enhanced_topic)
            
            if not images or len(images) == 0:
                print("❌ No images found. Cannot create video without visuals.")
                return
            
            # Validate that image files exist
            valid_images = [img for img in images if os.path.exists(img)]
            
            if not valid_images:
                print("❌ No valid image files found.")
                return
            
            print(f"✓ Found {len(valid_images)} valid images")
            
        except Exception as e:
            print(f"❌ Image fetching failed: {e}")
            traceback.print_exc()
            return
        
        # Step 4: Create Video
        print("\n3️⃣  Assembling Video...")
        try:
            video_output = os.path.join(OUTPUT_DIR, "video.mp4")
            make_video(
                valid_images, 
                voice_path, 
                video_output
            )
            
            if os.path.exists(video_output):
                file_size = os.path.getsize(video_output) / (1024 * 1024)  # MB
                print(f"✓ Video created: {video_output} ({file_size:.2f} MB)")
            else:
                print(f"⚠️ Video file not found at {video_output}")
                
        except Exception as e:
            print(f"❌ Video assembly failed: {e}")
            traceback.print_exc()
            return
        
        # Step 5: Generate Thumbnails
        print("\n4️⃣  Generating Thumbnails...")
        try:
            generate_thumbnail_options(valid_images, topic)
        except Exception as e:
            print(f"⚠️ Thumbnail generation failed (non-critical): {e}")
        
        # Success!
        print("\n" + "=" * 50)
        print("🎉 VIDEO GENERATION COMPLETE!")
        print("=" * 50)
        print(f"\n📁 Output files in: {os.path.abspath(OUTPUT_DIR)}/")
        print(f"   - video.mp4")
        print(f"   - script.txt")
        print(f"   - voice.mp3")
        print(f"   - thumbnail images (if generated)")
        print("\n✨ Done! Check output/video.mp4")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()