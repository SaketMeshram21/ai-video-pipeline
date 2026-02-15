import os
import traceback
import whisper
from moviepy import (
    ImageClip, 
    AudioFileClip, 
    CompositeAudioClip, 
    TextClip, 
    CompositeVideoClip, 
    ColorClip,
    vfx
)

def resize_to_fill(clip, width=1920, height=1080):
    """
    Smartly resizes an image to fill the screen without stretching.
    - If image is too wide, it crops the sides.
    - If image is too tall, it crops the top/bottom.
    
    Args:
        clip: MoviePy ImageClip
        width: Target width (default 1920)
        height: Target height (default 1080)
    
    Returns:
        Resized and cropped clip
    """
    try:
        ratio_clip = clip.w / clip.h
        ratio_target = width / height

        if ratio_clip > ratio_target:
            # Image is wider than 16:9 -> Resize by height, crop sides
            new_clip = clip.resized(height=height)
            return new_clip.cropped(
                x_center=new_clip.w/2, 
                y_center=new_clip.h/2, 
                width=width, 
                height=height
            )
        else:
            # Image is taller/squarer -> Resize by width, crop vertical
            new_clip = clip.resized(width=width)
            return new_clip.cropped(
                x_center=new_clip.w/2, 
                y_center=new_clip.h/2, 
                width=width, 
                height=height
            )
    except Exception as e:
        print(f"⚠️ Error resizing clip: {e}")
        # Fallback: just resize without smart cropping
        return clip.resized((width, height))

def get_system_font():
    """
    Find an available system font by testing actual font files
    
    Returns:
        Full path to font file or None for default
    """
    import os
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
                print(f"   ✓ Found working font: {os.path.basename(font_path)}")
                return font_path
            except Exception as e:
                continue
    
    # If no font found, return None and let MoviePy use default
    print("   ⚠️ No custom font found, using system default")
    return None

def add_subtitles_precomputed(video_clip, result):
    """
    Add subtitles to video based on Whisper transcription results
        - Uses pre-computed segments from transcription
        - Smart-wraps text to fit within safe area
        - Handles font issues gracefully
        - Returns a CompositeVideoClip with subtitles layered on top
        - If subtitle creation fails, returns original video clip without subtitles
    """
    print("✏️ Adding Smart-Wrap Subtitles...")
    subtitle_clips = []
    
    # Define a safe text area (10% padding on sides)
    safe_width = 1700
    
    if 'segments' not in result:
        print("⚠️ No segments found in transcription result")
        return video_clip
    
    # Find a working font (returns full path or None)
    working_font = get_system_font()

    for i, segment in enumerate(result['segments']):
        try:
            text = segment.get('text', '').strip()
            
            if not text:
                continue
            
            start_time = segment.get('start', 0)
            end_time = segment.get('end', start_time + 2)
            
            # Create the Text with proper font handling
            # Build parameters WITHOUT font first
            txt_params = {
                'text': text,
                'font_size': 45,  
                'color': 'yellow',
                'stroke_color': 'black',
                'stroke_width': 2,  # Reduced from 3 to 2
                'method': 'caption',
                'size': (safe_width, None),
                'text_align': 'center'
            }
            
            # Only add font if we have a valid path
            if working_font:
                txt_params['font'] = working_font
            
            try:
                txt = (TextClip(**txt_params)
                    .with_start(start_time)
                    .with_duration(end_time - start_time)
                    .with_position(('center', 0.65), relative=True)) #0.75 to 65 
                
                subtitle_clips.append(txt)
            except Exception as font_error:
                # If font fails, try without any font (system default)
                if 'font' in txt_params:
                    print(f"   ⚠️ Font failed for segment {i}, trying default font")
                    del txt_params['font']
                    try:
                        txt = (TextClip(**txt_params)
                            .with_start(start_time)
                            .with_duration(end_time - start_time)
                            .with_position(('center', 0.65), relative=True)) #0.72 to 65
                        
                        subtitle_clips.append(txt)
                    except Exception as e2:
                        print(f"   ⚠️ Could not create subtitle {i} even with default font: {e2}")
                        continue
                else:
                    print(f"   ⚠️ Could not create subtitle {i}: {font_error}")
                    continue
            
        except Exception as e:
            print(f"⚠️ Error creating subtitle for segment {i}: {e}")
            continue

    if subtitle_clips:
        print(f"✓ Added {len(subtitle_clips)} subtitle segments")
        return CompositeVideoClip([video_clip] + subtitle_clips, size=video_clip.size)
    else:
        print("⚠️ No subtitles were added - continuing without subtitles")
        return video_clip

def load_whisper_model(model_size="base"):
    """
    Load Whisper model with error handling
    
    Args:
        model_size: Size of model to load (tiny, base, small, medium, large)
    
    Returns:
        Loaded Whisper model or None
    """
    try:
        print(f"⏳ Loading Whisper model ({model_size})...")
        model = whisper.load_model(model_size, device="cpu")
        print("✓ Whisper model loaded")
        return model
    except Exception as e:
        print(f"❌ Failed to load Whisper model: {e}")
        traceback.print_exc()
        return None

def transcribe_audio(model, audio_path):
    """
    Transcribe audio file using Whisper
    
    Args:
        model: Loaded Whisper model
        audio_path: Path to audio file
    
    Returns:
        Transcription result dictionary or None
    """
    try:
        print(f"⏳ Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path, fp16=False)
        
        if 'segments' in result and len(result['segments']) > 0:
            print(f"✓ Transcription complete: {len(result['segments'])} segments")
            return result
        else:
            print("⚠️ Transcription returned no segments")
            return None
            
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        traceback.print_exc()
        return None

def make_video(images, voice_path, output_path="output/video.mp4"):
    """
    Assemble final video from images and voice (no background music)
    
    Args:
        images: List of image file paths
        voice_path: Path to voice audio file
        output_path: Output video file path
    """
    print("🎬 Starting Pro Video Assembly (Smart Fit & Sync)...")
    
    # Input validation
    if not images:
        raise ValueError("No images provided")
    
    if not os.path.exists(voice_path):
        raise FileNotFoundError(f"Voice file not found: {voice_path}")
    
    # Validate images exist
    valid_images = [img for img in images if os.path.exists(img)]
    if not valid_images:
        raise ValueError("No valid image files found")
    
    if len(valid_images) < len(images):
        print(f"⚠️ Warning: {len(images) - len(valid_images)} images not found, using {len(valid_images)}")
    
    images = valid_images
    
    try:
        # 1. Audio Setup
        print("⏳ Loading audio...")
        voice_audio = AudioFileClip(voice_path)
        total_duration = voice_audio.duration + 0.5  # Small buffer
        print(f"✓ Voice duration: {total_duration:.2f}s")
        
        # 2. Transcribe audio
        model = load_whisper_model("base")
        if model is None:
            raise Exception("Failed to load Whisper model")
        
        result = transcribe_audio(model, voice_path)
        if result is None or 'segments' not in result or len(result['segments']) == 0:
            raise Exception("Transcription failed or returned no segments")
        
        segments = result['segments']
        print(f"✓ Processing {len(segments)} transcript segments")
        
        # 3. Build video clips timeline
        print("⏳ Creating video clips...")
        processed_clips = []
        crossfade_dur = 0.5
        
        for i, segment in enumerate(segments):
            if i >= len(images):
                print(f"⚠️ More segments ({len(segments)}) than images ({len(images)}), stopping at image {i}")
                break
            
            try:
                start_t = segment.get('start', 0)
                
                # Determine Duration (No Gaps Logic)
                if i == len(segments) - 1 or i == len(images) - 1:
                    # Last clip stretches to the very end
                    duration = total_duration - start_t
                else:
                    # Clips bridge to the next start time
                    next_start = segments[i+1].get('start', start_t + 3)
                    duration = next_start - start_t
                
                # Ensure positive duration
                if duration <= 0:
                    duration = 3.0  # Minimum 3 seconds
                
                # Load and resize image
                raw_img = ImageClip(images[i])
                
                # Apply Smart Fill (Fixes the "Zoomed/Stretched" issue)
                clip = resize_to_fill(raw_img, 1920, 1080)
                
                # Set timing
                clip = clip.with_start(start_t).with_duration(duration + crossfade_dur)
                
                # Apply Smooth Crossfade (except first)
                if i > 0:
                    clip = clip.with_effects([vfx.CrossFadeIn(crossfade_dur)])
                
                processed_clips.append(clip)
                
                print(f"   ✓ Clip {i+1}/{min(len(segments), len(images))}: {start_t:.2f}s - {start_t + duration:.2f}s")
                
            except Exception as e:
                print(f"⚠️ Error processing image {i} ({images[i]}): {e}")
                continue
        
        if not processed_clips:
            raise Exception("No video clips were successfully created")
        
        print(f"✓ Created {len(processed_clips)} video clips")
        
        # 4. Create background base (black layer for fail-safe)
        print("⏳ Compositing video...")
        bg_base = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=total_duration)
        
        # 5. Composite video layers
        video_track = CompositeVideoClip([bg_base] + processed_clips, size=(1920, 1080))
        
        # 6. Add subtitles
        video_final = add_subtitles_precomputed(video_track, result)
        
        # 7. Set audio (voice only, no background music)
        print("⏳ Setting audio...")
        final_audio = voice_audio
        
        # 8. Export final video
        print(f"🚀 Rendering final video to {output_path}...")
        print("   This may take several minutes...")
        
        output = video_final.with_audio(final_audio).with_duration(voice_audio.duration)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check MoviePy version and use appropriate parameters
        try:
            # Try new MoviePy API (v2.0+)
            output.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                preset="medium",
                threads=4
            )
        except TypeError as e:
            if 'verbose' in str(e) or 'logger' in str(e):
                # Fallback for older MoviePy versions
                print("   (Using legacy MoviePy parameters)")
                output.write_videofile(
                    output_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac",
                    preset="medium",
                    threads=4,
                    verbose=False,
                    logger=None
                )
            else:
                raise
        
        # Cleanup
        print("⏳ Cleaning up...")
        output.close()
        voice_audio.close()
        video_final.close()
        video_track.close()
        bg_base.close()
        
        for clip in processed_clips:
            clip.close()
        
        

        print("✅ Video assembly complete!")
        
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        traceback.print_exc()
        raise