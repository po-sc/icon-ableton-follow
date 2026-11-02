# === CONTROLLER MODE BUFFER ===
class SharedModeBuffer:
    def __init__(self):
        self.current_mode = "standard_mode"

    def set_mode(self, mode):
        self.current_mode = mode
        print(f"[ModeBuffer] Mode set to: {self.current_mode}")

    def get_mode(self):
        return self.current_mode

shared = SharedModeBuffer()
