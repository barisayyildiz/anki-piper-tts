from aqt import mw
from aqt.qt import *
from .piper_manager import get_voices_dir
from .downloader_dialog import VoiceDownloaderDialog

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Piper TTS Settings")
        
        # Get the base addon folder name
        self.addon_name = __name__.split('.')[0]
        self.config = mw.addonManager.getConfig(self.addon_name) or {}
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.fields_to_process_input = QLineEdit(self.config.get("fields_to_process", "Text, Audio"))
        
        self.default_voice_input = QComboBox()
        self.default_voice_input.setEditable(True)
        current_voice = self.config.get("default_voice", "en_US-lessac-medium")
        
        available_voices = set()
        voices_dir = get_voices_dir()
        if voices_dir.exists():
            for f in voices_dir.iterdir():
                if f.is_file() and f.name.endswith(".onnx"):
                    # Remove the .onnx extension to get the voice name
                    available_voices.add(f.stem)
                    
        available_voices.add(current_voice)
        self.default_voice_input.addItems(sorted(list(available_voices)))
        self.default_voice_input.setCurrentText(current_voice)
        
        self.download_voices_btn = QPushButton("Download New Voices...")
        self.download_voices_btn.clicked.connect(self.open_downloader)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(self.default_voice_input)
        voice_layout.addWidget(self.download_voices_btn)
        
        self.override_audio_checkbox = QCheckBox()
        self.override_audio_checkbox.setChecked(self.config.get("override_audio", False))
        
        form_layout.addRow("Fields to process (comma-separated):", self.fields_to_process_input)
        form_layout.addRow("Default Voice:", voice_layout)
        form_layout.addRow("Override existing audio:", self.override_audio_checkbox)
        
        layout.addLayout(form_layout)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        
        layout.addWidget(btn_box)
        self.setLayout(layout)
        self.resize(400, 200)
        
    def accept(self):
        self.config["fields_to_process"] = self.fields_to_process_input.text()
        self.config["default_voice"] = self.default_voice_input.currentText()
        self.config["override_audio"] = self.override_audio_checkbox.isChecked()
        
        mw.addonManager.writeConfig(self.addon_name, self.config)
        super().accept()

    def open_downloader(self):
        dialog = VoiceDownloaderDialog(self)
        dialog.exec()
        self.refresh_voices()

    def refresh_voices(self):
        current_voice = self.default_voice_input.currentText()
        self.default_voice_input.clear()
        
        available_voices = set()
        voices_dir = get_voices_dir()
        if voices_dir.exists():
            for f in voices_dir.iterdir():
                if f.is_file() and f.name.endswith(".onnx"):
                    available_voices.add(f.stem)
                    
        if current_voice:
            available_voices.add(current_voice)
            
        self.default_voice_input.addItems(sorted(list(available_voices)))
        self.default_voice_input.setCurrentText(current_voice)
