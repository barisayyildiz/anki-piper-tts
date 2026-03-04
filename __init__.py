from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
import os

from . import editor_integration
from . import browser_integration
from .settings_dialog import SettingsDialog

def show_settings():
    dialog = SettingsDialog(mw)
    dialog.exec()

def init_addon():
    # Initialize components
    editor_integration.init_editor()
    browser_integration.init_browser()
    
    # Add settings menu item under Tools
    action = QAction("Piper TTS Settings", mw)
    qconnect(action.triggered, show_settings)
    mw.form.menuTools.addAction(action)

# Initialize when Anki is ready
init_addon()
