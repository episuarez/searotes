import time
import webbrowser

from flask import Flask, escape, redirect, render_template, request, url_for

from sources import Sources

app = Flask(__name__);

path_documents = "";

sources = Sources(path_documents);

@app.route("/")
def index():
    results = [];
    seconds = None;

    if request.args.get("search") != None and request.args.get("search") != "" and len(request.args.get("search")) > 2:
        search = request.args.get("search");
        before = time.time();
        results = sources.search(search);
        seconds = f"Tiempo de busqueda: {round(time.time() - before, 2)} segundos";
    else:
        search = "";

    return render_template("index.html", seconds=seconds, search=search, results=results, numero_documentos=len(sources.documents), path_documents=path_documents);

@app.route("/change_path/<path:path>")
def change_path(path):
    global path_documents, sources;

    path_documents = escape(path);
    sources = Sources(path_documents);
    
    return redirect(url_for('index'));

if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:5000");
    app.run();
