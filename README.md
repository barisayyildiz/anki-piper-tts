# Piper TTS Anki Addon

Anki add-on that provides high-quality, offline Text-to-Speech (TTS) generation using [Piper TTS](https://github.com/rhasspy/piper). Generate natural-sounding audio for your Anki cards directly from your text fields, completely offline.

## Features

- **Offline TTS**: Fast, private, and offline audio generation.
- **Auto-Download**: Automatically downloads the necessary Piper executable and voice models if they aren't provided.
- **Bulk Audio Generation (Browser)**: Select multiple cards in the Anki Browser, right-click, and generate audio for multiple fields at once.
- **Single-Field Audio Generation (Editor)**: Use the toolbar button (or keyboard shortcut) in the note editor to generate and append audio for the currently focused text field.
- **Multi-Field Support**: Configure multiple fields to process simultaneously during bulk generation. Audio is smoothly appended to the end of each field.

## Installation

*(Note: If this add-on is available on AnkiWeb, the standard code installation process applies. If installing manually from source, place the `anki-piper-tts` folder into your Anki `addons21` directory.)*

## Usage

### In the Card Editor
1. Click inside any text field on your note.
2. Click the **🎧** button in the editor's formatting toolbar, or use the keyboard shortcut `Ctrl+Shift+P`.
3. The add-on will read the text from that specific field, generate an audio file, and append the `[sound:...]` tag to the end of your field content.

### In the Card Browser (Bulk Generation)
1. Open the Anki Browser and select the cards you want to process.
2. Right-click the selected cards and choose **"Generate Audio (Piper TTS)"**.
3. The add-on will process each specified field (configured in the Add-on Settings) for all selected notes, appending the generated audio to the end of each matching field.

## Configuration

You can configure the add-on by going to **Tools > Add-ons**, selecting **Piper TTS Anki Addon**, and clicking **Config**.

- **Fields to process (comma-separated)** (`fields_to_process`):
  A comma-separated list of field names. During bulk browser generation, the add-on reads text from each of these fields and appends the generated audio tag to the end of the same field. (Example: `Text, Sentence, Extra`)

- **Default Voice** (`default_voice`):
  The voice model to use for TTS. Make sure to use the exact Huggingface model format. For example: `en_US-lessac-medium`, `de_DE-thorsten-medium`, etc.

- **Piper Executable Path (Optional)** (`piper_executable_path`):
  If you already have Piper installed on your machine and want to skip downloading it, you can provide the full absolute path to your local `piper` executable.
  - Leave empty (`""`) to maintain the default behavior (the add-on downloads Piper automatically).
  - Example: `"/usr/bin/piper"` or `"C:\\piper\\piper.exe"`

## Troubleshooting

- **No audio generated**: Ensure that the configured fields exactly match the field names in your Note Type. Check your internet connection the first time you use a new voice or run the add-on, as it needs to download Piper and the model files.
- **Voice model not found**: Ensure the voice name is typed correctly in the configuration according to Piper's supported voices list.
- **Check the Console**: If you encounter errors, check the Anki developer console (`Tools > Add-ons > "View Files"`... or start Anki from terminal) for specific Piper startup logs.
