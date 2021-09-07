import glob
import logging
from logging.handlers import RotatingFileHandler
import os
import time

import wikipedia
from requests_html import HTMLSession
from whoosh import fields, index
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.support.charset import accent_map

from core.documents import Document

if not os.path.exists("logs"):
    os.mkdir("logs");

logging.basicConfig(
    format="%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s",
    level=logging.INFO,
    handlers=[RotatingFileHandler("logs/info.log", maxBytes=5 * 1024 * 1024, backupCount=3)]
);

wikipedia.set_lang("es");

class Core:
    def __init__(self):
        self.surround = 400;

        self.check = {"wikipedia": True, "daypo": True, "documents": True};

        self.remove_dir("uploads/*");
        self.remove_dir("index_dir/*");

        my_analyzer = StemmingAnalyzer() | CharsetFilter(accent_map);
        self.schema = fields.Schema(title=fields.TEXT(stored=True), path=fields.ID(stored=True), content=fields.TEXT(stored=True, analyzer=my_analyzer));

        if not os.path.exists("index_dir"):
            os.mkdir("index_dir");
        self.index_small = create_in("index_dir", self.schema, indexname="small");
        self.index_big = create_in("index_dir", self.schema, indexname="big");

        index.exists_in("index_dir", indexname="small");
        index.exists_in("index_dir", indexname="big");

    def remove_dir(self, dir):
        files = glob.glob(dir)
        for file in files:
            os.remove(file);

    def index_wikipedia(self, text):
        try:
            logging.info(f"Se comienza a buscar en la wikipedia {text}");
            search = wikipedia.page(text);

            writer = self.index_small.writer();
            writer.add_document(title=f"Wikipedia {text}", path=search.url, content=search.content);
            writer.commit();

            logging.info(f"Se acaba a buscar en la wikipedia {text}");
        except Exception as error:
            logging.error(f"Ha habido un error al buscar {text} en la wikipedia. {error}");

    def index_daypo(self, text):
        logging.info(f"Se comienza a buscar en daypo {text}");

        session = HTMLSession();
        result = session.get(f"https://www.google.com/search?q={text}+site:daypo.com");

        if result.status_code != 200:
            logging.error(f"Ha habido un error al consultar {text} en la página de google. {result.status_code}");
        else:
            for posicion in range(1, 10):
                titulo = result.html.xpath(f"//*[@id='rso']/div[{posicion}]/div/div/div[1]/a/h3/text()");
                url = result.html.xpath(f"//*[@id='rso']/div[{posicion}]/div/div/div[1]/a/@href");

                if len(url) == 0:
                    logging.info(f"No hay resultados en google de {text}");
                else:
                    result_daypo = session.get(url[0]);

                    if result_daypo.status_code != 200:
                        logging.error(f"Ha habido un error al consultar {text} en la página {url[0]} en daypo. {result.status_code}");
                    else:
                        writer = self.index_small.writer();
                        writer.add_document(title=titulo[0], path=url[0], content=result_daypo.html.xpath(f"//*[@class='w tal']/tr/td")[0].text);
                        writer.commit();
        
        logging.info(f"Se acaba a buscar en la daypo {text}");

    def index_documents(self, name, path):
        document = Document(path);
        writer = self.index_big.writer();
        writer.add_document(title=name, path=path, content=str(document.text));
        writer.commit();

    def search(self, text, wikipedia=True, daypo=True):
        documents_search = [];
        index.exists_in("index_dir", indexname="small");
        
        before = time.time();
        logging.info("Comienza la indexacion");

        if wikipedia and self.check["wikipedia"]:
            self.index_wikipedia(text);
        
        if daypo and self.check["daypo"]:
            self.index_daypo(text);

        index_time = round(time.time() - before, 2);
        logging.info(f"Finaliza la indexacion {index_time}");

        before = time.time();
        logging.info("Comienza la busqueda");

        with self.index_small.searcher() as searcher:
            query = QueryParser("content", self.index_small.schema).parse(f'"{text}"');
            results = searcher.search(query, limit=None);

            results.fragmenter.surround = self.surround;

            for result in results:
                documents_search.append({
                    "title": result["title"],
                    "path": result["path"],
                    "content": result.highlights("content")
                });

        if self.check["documents"]:
            with self.index_big.searcher() as searcher:
                query = QueryParser("content", self.index_big.schema).parse(f'"{text}"');
                results = searcher.search(query, limit=None);

                results.fragmenter.surround = self.surround;

                for result in results:
                    documents_search.append({
                        "title": result["title"],
                        "path": result["path"],
                        "content": result.highlights("content")
                    });

        search_time = round(time.time() - before, 2);
        logging.info(f"Finaliza la busqueda {search_time}");

        return (documents_search, index_time, search_time);
        