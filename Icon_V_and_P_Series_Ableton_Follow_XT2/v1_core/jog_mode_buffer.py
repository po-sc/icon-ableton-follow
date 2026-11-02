# === JOG MODE BUFFER ===
class SharedJogModeBuffer:
    def __init__(self):
        self.current_mode = "jog_standard_mode"

    def set_mode(self, mode):
        self.current_mode = mode
        print(f"[JogModeBuffer] Mode set to: {self.current_mode}")

    def get_mode(self):
        return self.current_mode

shared = SharedJogModeBuffer()
