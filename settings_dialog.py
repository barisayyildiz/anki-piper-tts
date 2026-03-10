from aqt import mw
from aqt.qt import *

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
        self.piper_exe_input = QLineEdit(self.config.get("piper_executable_path", ""))
        self.default_voice_input = QLineEdit(self.config.get("default_voice", "en_US-lessac-medium"))
        
        self.override_audio_checkbox = QCheckBox()
        self.override_audio_checkbox.setChecked(self.config.get("override_audio", False))
        
        form_layout.addRow("Fields to process (comma-separated):", self.fields_to_process_input)
        form_layout.addRow("Piper Executable Path (Optional):", self.piper_exe_input)
        form_layout.addRow("Default Voice:", self.default_voice_input)
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
        self.config["piper_executable_path"] = self.piper_exe_input.text()
        self.config["default_voice"] = self.default_voice_input.text()
        self.config["override_audio"] = self.override_audio_checkbox.isChecked()
        
        mw.addonManager.writeConfig(self.addon_name, self.config)
        super().accept()
