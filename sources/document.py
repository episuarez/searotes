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

        self.text = self.get_text_normalize(self.document.get_text());

        self.tokens = [self.clean_text(word) for word in self.text.split(" ")];
        self.tokens = [word for word in self.tokens if word != ""];

    def search(self, search_text, lenght=100):
        search_text = self.get_text_normalize(search_text);
        number_words = search_text.count(" ") + 1;
        positions = [];

        if number_words > 1:
            words = search_text.split(" ");

            if words[0] in self.tokens:
                for position, value in enumerate(self.tokens):
                    if words[0] == value:
                        
                        words_iterator = self.tokens[position:position + number_words];

                        if "".join(words_iterator) == "".join(words):
                            positions.append(position);  
        else:
            if search_text in self.tokens:
                for position, value in enumerate(self.tokens):
                    if search_text == value:
                        positions.append(position);

        for position, value in enumerate(positions):

            duplicado = False;
            for other_position, other_value in enumerate(positions):
                if position != other_position:
                    if value > other_value - lenght and value < other_value + lenght:
                        duplicado = True;
            
            if duplicado:
                positions.remove(value);
        
        results = [];
        if len(positions) > 0:
            for position in positions:
                minimo = 0 if position - lenght < 0 else position - lenght;
                maximo = len(self.text) if position + lenght > len(self.text) else position + lenght;
                data = " ".join(self.tokens[minimo:maximo]);

                if len(data) > 0:
                    data = data.replace(search_text, f"<span class='search'>{search_text}</span>");
                    results.append(data);

        return results;

    def clean_text(self, text):
        text = "".join([word for word in text if word.isalnum()]);
        text = text.replace("\n", "");
        return text;

    def get_text_normalize(self, text):
        return ''.join(character for character in unicodedata.normalize("NFKD", text) if unicodedata.category(character) != 'Mn').lower();
