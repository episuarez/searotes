import os
import threading

import webview
from flask import Flask, render_template, request, redirect, url_for, escape

from documents import Documents

app = Flask(__name__);

path_documents = "";

documents = Documents(path_documents);

@app.route("/")
def index():
    results = [];

    if request.args.get("search") != None and request.args.get("search") != "" and len(request.args.get("search")) > 2:
        search = request.args.get("search");
        results = documents.search(search);
    else:
        search = "";

    return render_template("index.html", search=search, results=results, numero_documentos=len(documents.documents), path_documents=path_documents);

@app.route("/change_path/<path:path>")
def change_path(path):
    global path_documents, documents;

    path_documents = escape(path);
    documents = Documents(path_documents);
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run();
