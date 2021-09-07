from os import read
import PyPDF2

class Pdf:
    def __init__(self, fullpath):
        self.fullpath = fullpath;

    def get_text(self):
        file = open(self.fullpath, "rb");
        reader = PyPDF2.PdfFileReader(file, strict=False);
        pages = reader.getNumPages();

        text = "";
        for page in range(1, pages):
            text += reader.getPage(page).extractText();

        file.close();

        return text;
