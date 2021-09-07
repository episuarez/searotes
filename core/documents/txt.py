class Txt:
    def __init__(self, fullpath):
        self.fullpath = fullpath;

    def get_text(self):
        with open(self.fullpath, "r", encoding="UTF-8", errors=None) as file:
            return file.read();
