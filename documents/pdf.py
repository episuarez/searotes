import PyPDF2

class Pdf:
    def __init__(self, fullpath):
        self.fullpath = fullpath;

    def get_text(self):
        reader = PyPDF2.PdfFileReader(self.fullpath);
        pages = reader.getNumPages();
        return reader.getPage(1-pages).extractText();
