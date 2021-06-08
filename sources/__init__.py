import os
import re
import time

import wikipedia
from requests_html import HTMLSession
from textblob import TextBlob

from .document import Document


class Sources:
    def __init__(self, path):
        self.path = path;
        self.documents = [];

        wikipedia.set_lang("es");

        self.load_data();

    def load_wikipedia(self, text):
        data = "";

        try:
            search = wikipedia.page(text);
            data = {
                "url": search.url, 
                "data": search.content[:1000].replace(text, f"<span class='search'>{text}</span>")
            };
        except:
            print(f"Búsqueda con múltiples resultados. {text}");

        return data;

    def load_documents(self, text):
        documents_search = [];
        for document in self.documents:
            data = document.search(text);

            for result in data:
                documents_search.append({
                    "fullpath": document.fullpath,
                    "file": document.name + document.extension,
                    "data": result,
                    "cantidad": result.count(text)
                });

        documents_search.sort(key=lambda result: result["cantidad"], reverse=True);

        return documents_search[:10];

    def load_daypo(self, text):
        session = HTMLSession();
        result = session.get(f"https://www.google.com/search?q={text}+site:daypo.com");

        documents_daypo = [];
        for posicion in range(1, 10):
            titulo = result.html.xpath(f"//*[@id='rso']/div[{posicion}]/div/div/div[1]/a/h3/text()");
            url = result.html.xpath(f"//*[@id='rso']/div[{posicion}]/div/div/div[1]/a/@href");

            if len(url) > 0:
                result_daypo = session.get(url[0]);
                description = TextBlob(result_daypo.html.xpath(f"//*[@class='w tal']/tr/td")[0].text);

                positions = [];
                for indice, valor in enumerate(description.sentences):
                    position = valor.find(text);
                    if position != -1:
                        positions.append(indice);

                results = [];
                if len(positions) > 0:
                    for position in positions:
                        data = "".join([sentence.string for sentence in description.sentences[position - 2:position + 3]]);
                        data = re.sub(text, f"<span class='search'>{text}</span>", data, flags=re.IGNORECASE);
                        results.append(data);

                documents_daypo.append({
                    "title": titulo[0],
                    "url": url[0],
                    "description": results
                });

        return documents_daypo;

    def load_data(self):
        before = time.time();

        if os.path.exists(self.path):
            documents = [os.path.join(dp, f) for dp, _, filenames in os.walk(self.path) for f in filenames if os.path.splitext(f)[1] in [".pdf", ".docx", ".pptx"]];

            extensions = [];
            for document in documents:
                extensions.append(os.path.splitext(os.path.basename(document))[1]);
                self.documents.append(Document(document));

            print(f"Tiempo de lectura de {len(documents)} documentos: {round(time.time() - before, 2)} segundos");
            print(f"Documentos: {list(set(extensions))}");
    
    def search(self, text):
        results = {};

        results.update({"wikipedia": self.load_wikipedia(text)});
        results.update({"documents": self.load_documents(text)});
        results.update({"daypo": self.load_daypo(text)});

        return results;
