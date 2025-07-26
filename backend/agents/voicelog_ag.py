from autogen import ConversableAgent
from backend.tools.whisper_transcriber import transcribe_and_tag

class VoiceLogAgent(ConversableAgent):
    def __init__(self, name="VoiceLogAgent"):
        super().__init__(name=name)

    def handle_voice(self, audio_path: str) -> dict:
        return transcribe_and_tag(audio_path)
