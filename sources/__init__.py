import os
import time
from multiprocessing import Pool

import wikipedia
from requests_html import HTMLSession

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
            data = document.search(text, 75);

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

            result_daypo = session.get(url[0]);
            description = result_daypo.html.xpath(f"//*[@class='w tal']/tr/td")[0].text.lower();

            documents_daypo.append({
                "title": titulo[0],
                "url": url[0],
                "description": description.replace(text, f"<span class='search'>{text}</span>")
            });

        return documents_daypo;

    def load_data(self):
        antes = time.time();

        if os.path.exists(self.path):
            documents = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.path) for f in filenames if os.path.splitext(f)[1] == '.pdf' or os.path.splitext(f)[1] == ".docx"];

            for document in documents:
                self.documents.append(Document(document));

        print(time.time() - antes);
    
    def search(self, text):
        results = {};

        results.update({"wikipedia": self.load_wikipedia(text)});
        results.update({"documents": self.load_documents(text)});
        results.update({"daypo": self.load_daypo(text)});

        return results;
