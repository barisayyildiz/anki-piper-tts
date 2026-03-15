# Piper TTS Configuration

This add-on connects to Piper TTS for audio generation.

## fields_to_process
A comma-separated list of fields to generate audio for. When clicking the bulk generation button in the browser, the add-on will read the text from each of these fields, generate the corresponding audio, and append the audio tag to the end of that same field.

## default_voice
The voice model to use for TTS. Ensure you use the exact huggingface model name (e.g., `en_US-lessac-medium`).

## override_audio
Enable this boolean value (`true` or `false`) to allow replacing existing audio in the specified fields. If false, existing generated audio is kept intact.
