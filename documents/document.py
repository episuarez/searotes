import os
import re
import unicodedata

from .docx import Docx
from .pdf import Pdf


class Document:
    def __init__(self, fullpath):
        self.fullpath = fullpath;
        self.name, self.extension = os.path.splitext(os.path.basename(self.fullpath));

        if self.extension == ".docx":
            self.document = Docx(self.fullpath);
        elif self.extension == ".pdf":
            self.document = Pdf(self.fullpath);

        self.text = self.document.get_text();

    def search(self, search_text, lenght=100):
        normalize_text = self.get_text_normalize(self.text);

        positions = [text.start() for text in re.finditer(search_text, normalize_text)];
        
        results = [];

        if len(positions) > 0:
            for position in positions:
                data = normalize_text[position - lenght:position + lenght];
                if len(data) > 0:
                    data = data.replace(search_text, f"<span class='search'>{search_text}</span>");
                    results.append(data);

        return results;

    def get_text_normalize(self, text):
        return ''.join(c for c in unicodedata.normalize("NFKD", text) if unicodedata.category(c) != 'Mn').lower();
