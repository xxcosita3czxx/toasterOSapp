#!/usr/bin/env python3
"""
Convert MP4 videos to individual frame images
This script will be used once to convert videos, then we can remove opencv dependency
"""

import cv2
import os
from PIL import Image

def convert_video_to_frames(video_path, output_dir, base_name):
    """Convert a video file to individual frame images"""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open {video_path}")
        return []
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Converting {video_path}:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {frame_count}")
    
    frame_files = []
    frame_num = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Save as PNG
        frame_filename = f"{base_name}_frame_{frame_num:04d}.png"
        frame_path = os.path.join(output_dir, frame_filename)
        pil_image.save(frame_path, 'PNG')
        
        frame_files.append(frame_filename)
        frame_num += 1
        
        if frame_num % 10 == 0:
            print(f"  Processed {frame_num}/{frame_count} frames...")
    
    cap.release()
    print(f"  Completed: {frame_num} frames saved")
    return frame_files

def main():
    """Convert all MP4 files in the load animation"""
    
    load_dir = os.path.join("Anims", "load")
    
    # Videos to convert
    videos = [
        ("start.mp4", "start"),
        ("between.mp4", "between"), 
        ("stop.mp4", "stop")
    ]
    
    converted_sequences = {}
    
    for video_file, base_name in videos:
        video_path = os.path.join(load_dir, video_file)
        
        if os.path.exists(video_path):
            print(f"\nConverting {video_file}...")
            frame_files = convert_video_to_frames(video_path, load_dir, base_name)
            converted_sequences[base_name] = frame_files
        else:
            print(f"Warning: {video_path} not found")
    
    # Print summary
    print("\n" + "="*50)
    print("CONVERSION SUMMARY:")
    print("="*50)
    
    for base_name, frames in converted_sequences.items():
        print(f"{base_name}: {len(frames)} frames")
        if frames:
            print(f"  First: {frames[0]}")
            print(f"  Last: {frames[-1]}")
    
    print("\nNow you can:")
    print("1. Update anim.json to use frame sequences instead of MP4 files")
    print("2. Remove opencv-python from requirements.txt") 
    print("3. Remove opencv imports from animations.py")

if __name__ == "__main__":
    main()
