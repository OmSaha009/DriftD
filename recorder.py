import whisper
import sounddevice as sd
import numpy as np
import keyboard
import tempfile
import wave
import os

class WhisperController:
    def __init__(self, model_size="base"):
        """Initialize Whisper model.
        
        Model sizes (trade accuracy for speed):
        - "tiny" (75MB) - Fastest, decent accuracy
        - "base" (145MB) - Good balance (recommended)
        - "small" (488MB) - Better accuracy, slower
        - "medium" (1.5GB) - Very accurate, slow
        - "large" (2.9GB) - Best accuracy, very slow
        """
        print(f"Loading Whisper '{model_size}' model (first time downloads)...")
        self.model = whisper.load_model(model_size)
        self.samplerate = 16000
        print("✅ Whisper ready!")
    
    def record_audio(self, duration=2.5, device=None):
        """Record audio from microphone."""
        print("🔴 Recording... Speak now!")
        
        recording = sd.rec(
            int(duration * self.samplerate),
            samplerate=self.samplerate,
            channels=1,
            dtype='float32',
            device=device
        )
        sd.wait()  # Wait for recording to finish
        
        # Whisper expects float32, values between -1 and 1
        return recording.flatten()
    
    def transcribe(self, audio_data):
        """Convert audio to text using Whisper."""
        print("🟢 Transcribing...")
        result = self.model.transcribe(audio_data, language="en")
        text = result["text"].strip().lower()
        return text
    
    def listen_once(self, duration=2.5, device=None):
        """Record and transcribe in one go."""
        audio = self.record_audio(duration, device)
        text = self.transcribe(audio)
        print(f"📝 Recognized: '{text}'")
        return text


class CommandParser:
    def __init__(self, controller):
        self.controller = controller
    
    def execute(self, command_text):
        """Parse and execute voice command."""
        text = command_text.lower().strip()
        
        if not text:
            return "Nothing heard"
        
        # Volume commands
        if any(phrase in text for phrase in ["volume up", "increase volume", "louder", "loud", "turn up"]):
            self.controller.volume_up()
            return "🔊 Volume increased"
        
        elif any(phrase in text for phrase in ["volume down", "decrease volume", "softer","soft", "turn down"]):
            self.controller.volume_down()
            return "🔉 Volume decreased"
        
        elif "mute" in text:
            self.controller.mute()
            return "🔇 Muted"
        
        # Brightness commands
        elif any(phrase in text for phrase in ["brightness up", "increase brightness", "brighter", "bright", "light"]):
            self.controller.brightness_up()
            return "☀️ Brightness increased"
        
        elif any(phrase in text for phrase in ["brightness down", "decrease brightness", "dimmer", "dim", "dark"]):
            self.controller.brightness_down()
            return "🌙 Brightness decreased"
        
        # Focus mode
        elif any(phrase in text for phrase in ["focus mode on", "focus on", "block sites", "distraction off"]):
            self.controller.focus_mode_on()
            return "🚫 Focus mode enabled"
        
        elif any(phrase in text for phrase in ["focus mode off", "focus off", "unblock sites", "distraction on"]):
            self.controller.focus_mode_off()
            return "✅ Focus mode disabled"
        
        else:
            return f"❓ Unknown command: '{command_text}'"