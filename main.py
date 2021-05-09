import os
import threading

import webview
from flask import Flask, render_template, request

from documents import Documents

app = Flask(__name__);

path_documents = "C:\\Users\\episu\\Desktop\\Derecho de los servicios públicos sociales\\";

documents = Documents(path_documents);

@app.route("/")
def index():
    results = [];

    if request.args.get("search") != None and request.args.get("search") != "" and len(request.args.get("search")) > 2:
        search = request.args.get("search");
        results = documents.search(search.split(" "));
    else:
        search = "";

    return render_template("index.html", search=search, results=results, numero_documentos=len(documents.documents), path_documents=path_documents);

#def launch_webserver():
app.run(debug=True);

"""webserver = threading.Thread(target=launch_webserver, daemon=True);
webserver.start();

window = webview.create_window("Searotes", "http://127.0.0.1:5000");
webview.start(window);"""
