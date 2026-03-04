import os
import sys
import subprocess
import hashlib
from pathlib import Path

from . import piper_manager
from aqt import mw

def generate_audio(text: str, voice_name: str, output_path: Path) -> bool:
    """
    Invokes the downloaded Piper executable to generate an audio file.
    Returns True if successful, False otherwise.
    """
    
    executable_path = piper_manager.get_piper_executable_path()
    model_path = piper_manager.get_voice_model_path(voice_name)
    
    if not executable_path.exists() or not model_path.exists():
        return False
        
    cmd = [
        str(executable_path),
        "--model", str(model_path),
        "--output_file", str(output_path)
    ]
    
    try:
        # Piper reads from stdin
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=text.encode('utf-8'))
        
        if process.returncode != 0:
            print(f"Piper error: {stderr.decode('utf-8')}")
            return False
            
        return output_path.exists()
        
    except Exception as e:
        print(f"Failed to run piper: {e}")
        return False

def generate_and_add_to_anki(text: str, voice_name: str) -> str:
    """
    Generates audio and copies it to the Anki media collection.
    Returns the sound tag, e.g., `[sound:piper_uuid.wav]`, or empty string if failed.
    """
    if not mw or not mw.col:
        return ""
        
    # Generate a unique filename based on hash of text + voice
    hash_str = hashlib.md5((text + voice_name).encode('utf-8')).hexdigest()[:10]
    filename = f"piper_{voice_name}_{hash_str}.wav"
    
    # We'll generate it to a temporary location first
    temp_dir = piper_manager.get_addon_dir() / "user_files" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_file_path = temp_dir / filename
    
    success = generate_audio(text, voice_name, temp_file_path)
    
    if not success:
        return ""
        
    try:
        # Move it to the media dir
        final_filename = mw.col.media.add_file(str(temp_file_path))
        if temp_file_path.exists():
            temp_file_path.unlink()
            
        return f"[sound:{final_filename}]"
    except Exception as e:
        print(f"Failed to add file to media collection: {e}")
        return ""
