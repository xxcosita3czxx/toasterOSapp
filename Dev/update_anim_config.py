#!/usr/bin/env python3
"""
Generate new anim.json with frame sequences instead of MP4 files
"""

import json
import os

def generate_frame_sequence(base_name, frame_count):
    """Generate a list of frame filenames for a video sequence"""
    return [f"{base_name}_frame_{i:04d}.png" for i in range(frame_count)]

def create_new_anim_config():
    """Create new animation config using frame sequences"""
    
    # Frame counts from conversion
    start_frames = generate_frame_sequence("start", 90)
    between_frames = generate_frame_sequence("between", 30) 
    stop_frames = generate_frame_sequence("stop", 30)
    
    # Create new animation sequence
    new_anim = []
    
    # Add start sequence
    new_anim.extend(start_frames)
    
    # Add the repeating between sequences with sleeps
    for i in range(6):  # 6 repetitions like in original
        new_anim.extend(between_frames)
        new_anim.append({"sleep": 1})
    
    # Add stop sequence
    new_anim.extend(stop_frames)
    new_anim.append({"sleep": 1})
    
    # Create the complete config
    config = {
        "anim": new_anim,
        "fill": "vertical",
        "interval": 1.0/30.0  # 30 FPS like original videos
    }
    
    return config

def main():
    """Update the anim.json file"""
    
    load_dir = os.path.join("Anims", "load")
    anim_json_path = os.path.join(load_dir, "anim.json")
    
    # Backup original
    backup_path = os.path.join(load_dir, "anim_original.json")
    if os.path.exists(anim_json_path):
        import shutil
        shutil.copy2(anim_json_path, backup_path)
        print(f"Backed up original to: {backup_path}")
    
    # Generate new config
    new_config = create_new_anim_config()
    
    # Save new config
    with open(anim_json_path, 'w') as f:
        json.dump(new_config, f, indent=2)
    
    print(f"Updated {anim_json_path}")
    print(f"Total animation items: {len(new_config['anim'])}")
    print(f"Frame interval: {new_config['interval']:.4f} seconds (30 FPS)")
    
    # Show first few and last few items
    print("\nFirst few items:")
    for i, item in enumerate(new_config['anim'][:5]):
        print(f"  {i}: {item}")
    
    print("\nLast few items:")
    for i, item in enumerate(new_config['anim'][-5:], len(new_config['anim'])-5):
        print(f"  {i}: {item}")

if __name__ == "__main__":
    main()
