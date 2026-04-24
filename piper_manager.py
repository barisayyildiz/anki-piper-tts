import os
import sys
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path

# Github release URLs for Piper
PIPER_VERSION = "2023.11.14-2"
PIPER_RELEASES = {
    "Windows": {
        "x86_64": f"https://github.com/rhasspy/piper/releases/download/{PIPER_VERSION}/piper_windows_amd64.zip"
    },
    "Darwin": {
        "x86_64": f"https://github.com/rhasspy/piper/releases/download/{PIPER_VERSION}/piper_macos_x64.tar.gz",
        "arm64": f"https://github.com/rhasspy/piper/releases/download/{PIPER_VERSION}/piper_macos_aarch64.tar.gz"
    },
    "Linux": {
        "x86_64": f"https://github.com/rhasspy/piper/releases/download/{PIPER_VERSION}/piper_linux_x86_64.tar.gz",
        "aarch64": f"https://github.com/rhasspy/piper/releases/download/{PIPER_VERSION}/piper_linux_aarch64.tar.gz"
    }
}

# Voice model URLs
# using rhasspy voices huggingface repo
VOICE_URLS = {
    "en_US-lessac-medium": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx?download=true",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json?download=true"
    },
    "de_DE-thorsten-medium": {
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx?download=true",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json?download=true"
    }
}

def get_addon_dir() -> Path:
    """Get the root directory of this addon."""
    from aqt import mw
    if mw is None:
        # Fallback for testing outside Anki
        return Path(__file__).parent.absolute()
    return Path(mw.addonManager.addonsFolder(mw.addonManager.addonFromModule(__name__)))

def get_piper_dir() -> Path:
    """Get the directory where the piper executable is stored."""
    base_dir = get_addon_dir() / "user_files" / "piper"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_voices_dir() -> Path:
    """Get the directory where voice models are stored."""
    base_dir = get_addon_dir() / "user_files" / "voices"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_piper_executable_path() -> Path:
    """Get the full path to the piper executable."""
    piper_dir = get_piper_dir()
    exe_name = "piper.exe" if platform.system() == "Windows" else "piper"
    
    # Check if the executable is inside the extracted folder
    direct_path = piper_dir / exe_name
    if direct_path.is_file():
        return direct_path
        
    extracted_path = piper_dir / "piper" / exe_name
    if extracted_path.is_file():
        return extracted_path

    return direct_path

def download_file(url: str, dest_path: Path):
    """Download a file with a basic progress print and UI event pumping."""
    print(f"Downloading {url} to {dest_path}...")
    def reporthook(blocknum, blocksize, totalsize):
        try:
            from aqt import mw
            if mw and mw.app:
                mw.app.processEvents()
        except:
            pass
            
    try:
        urllib.request.urlretrieve(url, dest_path, reporthook=reporthook)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        raise

def ensure_piper_executable() -> bool:
    """Downloads and extracts the piper executable for the current OS if not present."""
    exe_path = get_piper_executable_path()
    if exe_path.exists():
        if platform.system() != "Windows":
            try:
                os.chmod(exe_path, 0o755)
            except Exception:
                pass
        return True

    os_name = platform.system()
    arch = platform.machine().lower()
    
    # normalize arch
    if arch in ["amd64", "x86_64"]:
        arch = "x86_64"
    elif arch in ["arm64", "aarch64"]:
         if os_name == "Darwin":
             arch = "arm64"
         else:
             arch = "aarch64"
    
    if os_name not in PIPER_RELEASES or arch not in PIPER_RELEASES[os_name]:
        print(f"Unsupported OS/Architecture: {os_name} / {arch}")
        return False

    url = PIPER_RELEASES[os_name][arch]
    piper_dir = get_piper_dir()
    download_path = piper_dir / "piper_download.archive"
    
    try:
        download_file(url, download_path)
        
        # Extract
        if str(download_path).endswith('.zip') or url.endswith('.zip'):
             with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(piper_dir)
        elif str(download_path).endswith('.tar.gz') or url.endswith('.tar.gz'):
             with tarfile.open(download_path, 'r:gz') as tar_ref:
                 tar_ref.extractall(piper_dir)
                 
        # Ensure executable permissions on unix
        if os_name != "Windows":
             exe = get_piper_executable_path()
             if exe.exists():
                 os.chmod(exe, 0o755)
                 
    except Exception as e:
        print(f"Error setting up Piper: {e}")
        return False
    finally:
        if download_path.exists():
             download_path.unlink()
             
    return get_piper_executable_path().exists()

def ensure_voice(voice_name: str) -> bool:
    """Downloads the required .onnx and .onnx.json files for a given voice if not present."""
    voices_dir = get_voices_dir()
    onnx_path = voices_dir / f"{voice_name}.onnx"
    json_path = voices_dir / f"{voice_name}.onnx.json"
    
    # If the voice files already exist locally, we use them without downloading.
    if onnx_path.exists() and json_path.exists():
        return True

    if voice_name not in VOICE_URLS:
        print(f"Unknown voice: {voice_name}")
        return False
        
    success = True
    if not onnx_path.exists():
         try:
             download_file(VOICE_URLS[voice_name]["onnx"], onnx_path)
         except Exception:
             success = False
             
    if not json_path.exists():
         try:
             download_file(VOICE_URLS[voice_name]["json"], json_path)
         except Exception:
             success = False
             
    return success and onnx_path.exists() and json_path.exists()

def get_voice_model_path(voice_name: str) -> Path:
    """Returns the path to the ONNX model for a voice."""
    return get_voices_dir() / f"{voice_name}.onnx"

