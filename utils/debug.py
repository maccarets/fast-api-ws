class Debug:
    def __init__(self, name, enabled):
        self.name       = name
        self.enabled    = enabled

    def echo(self, message):
        if not self.enabled:
            return
        print(f"{self.name} {message}")