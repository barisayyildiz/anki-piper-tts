import os
import re
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning
from aqt.browser import Browser

from . import piper_manager
from . import tts

def on_bulk_generate(browser: Browser):
    """
    Handler for the context menu item in the Anki Browser.
    """
    selected_cids = browser.selectedCards()
    if not selected_cids:
        showWarning("No cards selected.")
        return
        
    config = mw.addonManager.getConfig(__name__)
    fields_str = config.get("fields_to_process", "Text, Audio")
    voice_name = config.get("default_voice", "en_US-lessac-medium")
    
    fields_list = [f.strip() for f in fields_str.split(",") if f.strip()]
    if not fields_list:
        showWarning("No fields specified for processing.")
        return

    # Step 1: Ensure Piper
    mw.progress.start(label="Checking Piper TTS executable...", immediate=True)
    executable_ready = piper_manager.ensure_piper_executable()
    mw.progress.finish()
    
    if not executable_ready:
        showWarning("Failed to setup Piper TTS executable.")
        return

    # Step 2: Ensure Voice
    mw.progress.start(label=f"Checking voice model ({voice_name})...", immediate=True)
    voice_ready = piper_manager.ensure_voice(voice_name)
    mw.progress.finish()
    
    if not voice_ready:
        showWarning(f"Failed to setup voice model '{voice_name}'.")
        return

    # Step 3: Process cards
    mw.progress.start(label="Generating audio for selected notes...", max=len(selected_cids), immediate=True)
    
    processed_notes = set() # Avoid doing the same note multiple times if multiple cards are selected
    success_count = 0
    fail_count = 0
    
    for _idx, cid in enumerate(selected_cids):
        mw.progress.update(value=_idx)
        card = mw.col.getCard(cid)
        note = card.note()
        
        if note.id in processed_notes:
            continue
            
        processed_notes.add(note.id)
        
        note_updated = False
        
        for field_name in fields_list:
            if field_name not in note.keys():
                continue
                 
            text = note[field_name]
            if not text.strip():
                continue
                
            clean_text = re.sub(r'\[sound:.*?\]', '', text)
            if not clean_text.strip():
                continue
                
            sound_tag = tts.generate_and_add_to_anki(clean_text, voice_name)
            if sound_tag:
                 if re.search(r'\[sound:.*?\]', text):
                     new_text = re.sub(r'\[sound:.*?\]', sound_tag, text, count=1)
                     note[field_name] = new_text
                 else:
                     note[field_name] = text + " " + sound_tag
                 note_updated = True
        
        if note_updated:
             note.flush()
             success_count += 1
        else:
             fail_count += 1

    mw.progress.finish()
    
    # Reload the browser rows
    browser.model.reset()
    mw.requireReset()
    
    showInfo(f"Finished bulk generation.\nNotes Updated: {success_count}.\nNotes Skipped/Failed: {fail_count}.")

def add_browser_menu_action(browser: Browser):
    """
    Hook to add a custom action to the right-click context menu in the browser.
    """
    menu = browser.form.menu_Cards
    action = QAction("Generate Audio (Piper TTS)", browser)
    action.triggered.connect(lambda _, b=browser: on_bulk_generate(b))
    menu.addAction(action)

def init_browser():
    from aqt.gui_hooks import browser_menus_did_init
    browser_menus_did_init.append(add_browser_menu_action)
