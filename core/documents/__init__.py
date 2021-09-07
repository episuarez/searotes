import os
import re

from .docx import Docx
from .pdf import Pdf
from .pptx import Pptx
from .txt import Txt

class Document:
    def __init__(self, fullpath):
        self.fullpath = fullpath;
        self.name, self.extension = os.path.splitext(os.path.basename(self.fullpath));

        if self.extension == ".docx":
            self.document = Docx(self.fullpath);
        elif self.extension == ".pptx":
            self.document = Pptx(self.fullpath);
        elif self.extension == ".pdf":
            self.document = Pdf(self.fullpath);
        elif self.extension == ".txt":
            self.document = Txt(self.fullpath);

        self.text = self.document.get_text();

    def search(self, search_text):
        positions = [];
        for indice, valor in enumerate(self.text.sentences):
            position = valor.find(search_text);
            if position != -1:
                positions.append(indice);
        
        results = [];
        if len(positions) > 0:
            for position in positions:
                data = "".join([sentence.string for sentence in self.text.sentences[position - 2:position + 3]]);
                data = re.sub(search_text, f"<span class='search'>{search_text}</span>", data, flags=re.IGNORECASE);
                results.append(data);

        return results;
