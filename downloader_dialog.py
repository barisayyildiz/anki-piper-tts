import urllib.request
import json
import os
from pathlib import Path

from aqt import mw
from aqt.qt import *

from .piper_manager import get_voices_dir

class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, voice_info):
        super().__init__()
        self.voice_info = voice_info
        self.is_cancelled = False

    def run(self):
        try:
            voices_dir = get_voices_dir()
            
            onnx_url = None
            json_url = None
            
            # The voice_info contains a 'files' dictionary
            # We need to find the .onnx and .onnx.json files
            for file_path, file_data in self.voice_info.get("files", {}).items():
                if file_path.endswith(".onnx"):
                    onnx_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/{file_path}?download=true"
                    onnx_dest = voices_dir / Path(file_path).name
                elif file_path.endswith(".onnx.json"):
                    json_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/{file_path}?download=true"
                    json_dest = voices_dir / Path(file_path).name

            if not onnx_url or not json_url:
                self.finished.emit(False, "Could not find model files in catalog.")
                return

            def report_progress(block_num, block_size, total_size):
                if self.is_cancelled:
                    raise Exception("Download cancelled by user")
                if total_size > 0:
                    percent = int(block_num * block_size * 100 / total_size)
                    self.progress.emit(min(percent, 100))

            # Download ONNX (main large file)
            self.progress.emit(0)
            urllib.request.urlretrieve(onnx_url, onnx_dest, reporthook=report_progress)
            
            # Download JSON config
            urllib.request.urlretrieve(json_url, json_dest)

            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))

    def cancel(self):
        self.is_cancelled = True


class VoiceDownloaderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download Piper Voices")
        self.resize(500, 300)
        self.voices_data = {}
        self.setup_ui()
        self.fetch_catalog()

    def setup_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.currentIndexChanged.connect(self.update_voice_names)
        form_layout.addRow("Language:", self.language_combo)

        self.name_combo = QComboBox()
        self.name_combo.currentIndexChanged.connect(self.update_qualities)
        form_layout.addRow("Voice Name:", self.name_combo)

        self.quality_combo = QComboBox()
        self.quality_combo.currentIndexChanged.connect(self.update_speaker_info)
        form_layout.addRow("Quality:", self.quality_combo)

        layout.addLayout(form_layout)

        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def fetch_catalog(self):
        self.status_label.setText("Fetching voice catalog...")
        self.language_combo.setEnabled(False)
        self.name_combo.setEnabled(False)
        self.quality_combo.setEnabled(False)

        # Do simple synchronous fetch for catalog since it's small json
        try:
            url = "https://huggingface.co/rhasspy/piper-voices/raw/v1.0.0/voices.json"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                self.voices_data = data
                self.populate_languages()
                self.status_label.setText("Catalog loaded.")
        except Exception as e:
            self.status_label.setText(f"Failed to load catalog: {e}")

    def populate_languages(self):
        languages = set()
        for voice_key, voice_info in self.voices_data.items():
            languages.add(voice_info.get("language", {}).get("name_english", "Unknown"))
        
        self.language_combo.clear()
        self.language_combo.addItems(sorted(list(languages)))
        
        self.language_combo.setEnabled(True)
        self.name_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)
        self.download_btn.setEnabled(True)

    def get_voices_for_language(self, language_name):
        voices = []
        for key, info in self.voices_data.items():
            if info.get("language", {}).get("name_english") == language_name:
                voices.append((key, info))
        return voices

    def update_voice_names(self):
        lang = self.language_combo.currentText()
        if not lang:
            return

        voices = self.get_voices_for_language(lang)
        names = set([info.get("name") for key, info in voices])
        
        self.name_combo.clear()
        self.name_combo.addItems(sorted(list(names)))

    def update_qualities(self):
        lang = self.language_combo.currentText()
        name = self.name_combo.currentText()
        if not lang or not name:
            return

        voices = self.get_voices_for_language(lang)
        qualities = []
        for key, info in voices:
            if info.get("name") == name:
                qualities.append(info.get("quality"))
                
        self.quality_combo.clear()
        # Sort qualities conceptually if possible, else alphabetically
        order = {"x_low": 0, "low": 1, "medium": 2, "high": 3}
        qualities.sort(key=lambda x: order.get(x, 99))
        self.quality_combo.addItems(qualities)

    def update_speaker_info(self):
        voice_info = self.get_selected_voice_info()
        if not voice_info:
            self.info_label.setText("")
            return
            
        speakers = voice_info.get("num_speakers", 1)
        speaker_text = "Single speaker" if speakers == 1 else f"Multiple speakers ({speakers})"
        
        dataset = voice_info.get("dataset", "Unknown dataset")
        self.info_label.setText(f"Dataset: {dataset}<br>{speaker_text}")

    def get_selected_voice_info(self):
        lang = self.language_combo.currentText()
        name = self.name_combo.currentText()
        quality = self.quality_combo.currentText()
        
        for key, info in self.voices_data.items():
            if (info.get("language", {}).get("name_english") == lang and
                info.get("name") == name and
                info.get("quality") == quality):
                return info
        return None

    def start_download(self):
        voice_info = self.get_selected_voice_info()
        if not voice_info:
            return

        self.download_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.language_combo.setEnabled(False)
        self.name_combo.setEnabled(False)
        self.quality_combo.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("Downloading...")

        self.worker = DownloadWorker(voice_info)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_download_finished)
        self.worker.start()

    def on_download_finished(self, success, error_msg):
        self.progress_bar.hide()
        self.close_btn.setEnabled(True)
        self.language_combo.setEnabled(True)
        self.name_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)
        self.download_btn.setEnabled(True)

        if success:
            self.status_label.setText("Download complete! You can select it now.")
            # Trigger accept so the parent dialog knows we might have new voices
            # but allow user to download more if they want? 
            # Let's just update text, user can close when ready.
        else:
            self.status_label.setText(f"Download failed: {error_msg}")

    def reject(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        super().reject()
