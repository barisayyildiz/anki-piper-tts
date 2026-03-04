import os
from aqt import mw
from aqt.editor import Editor
from aqt.qt import *
from aqt.utils import showInfo, showWarning, askUser

from . import piper_manager
from . import tts

def on_generate_audio(editor: Editor):
    """
    Called when the 'Generate Audio' button is clicked in the Anki Editor.
    Gets the text from the current field, generates audio, and updates the field.
    """
    # Current focused field
    current_field = editor.currentField
    
    if current_field is None:
        showWarning("Please select a field first.")
        return
        
    text = editor.note.fields[current_field]
    
    if not text.strip():
        showWarning("The selected field is empty.")
        return
        
    config = mw.addonManager.getConfig(__name__)
    voice_name = config.get("default_voice", "en_US-lessac-medium")

    # Step 1: Ensure executable exists
    mw.progress.start(label="Checking Piper TTS executable...", immediate=True)
    executable_ready = piper_manager.ensure_piper_executable()
    mw.progress.finish()
    
    if not executable_ready:
        showWarning("Failed to download or locate the Piper TTS executable. Check your internet connection or OS compatibility.")
        return

    # Step 2: Ensure voice model exists
    mw.progress.start(label=f"Checking voice model ({voice_name})...", immediate=True)
    voice_ready = piper_manager.ensure_voice(voice_name)
    mw.progress.finish()
    
    if not voice_ready:
        showWarning(f"Failed to download or locate the voice model '{voice_name}'.")
        return

    # Step 3: Generate Audio
    mw.progress.start(label="Generating audio...", immediate=True)
    sound_tag = tts.generate_and_add_to_anki(text, voice_name)
    mw.progress.finish()
    
    if sound_tag:
        # Append the sound tag to the field
        # Use editor.currentField and editor.loadNote() to refresh UI
        current_text = editor.note.fields[current_field]
        editor.note.fields[current_field] = current_text + " " + sound_tag
        editor.loadNote()
        # Optionally, save note immediately, but generally we let the user hit Save
    else:
        showWarning("Failed to generate audio. Check the error console or logs.")


def setup_buttons(buttons, editor: Editor):
    """
    Hook function to add our button to the Anki Editor toolbar.
    """
    config = mw.addonManager.getConfig(__name__)
    
    # We could optionally add an icon here, but text is fine for a first iteration
    btn = editor.addButton(
        icon=None,
        cmd="piper_tts",
        func=lambda o=editor: on_generate_audio(o),
        tip="Generate TTS Audio using Piper",
        keys="Ctrl+Shift+P", # Keyboard shortcut
        label="🎧",
        id="btn_piper_tts"
    )
    
    buttons.append(btn)
    return buttons

def init_editor():
    from anki.hooks import addHook
    addHook("setupEditorButtons", setup_buttons)
