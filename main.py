import os
import threading

import webview
from flask import Flask, render_template, request

from documents import Documents
from configuration import data

app = Flask(__name__);

documents = Documents(data["path"]);

@app.route("/")
def index():
    results = [];

    if request.args.get("search") != None and request.args.get("search") != "" and len(request.args.get("search")) > 2:
        search = request.args.get("search");
        results = documents.search(search);
    else:
        search = "";

    return render_template("index.html", search=search, results=results);

def launch_webserver():
    app.run();

webserver = threading.Thread(target=launch_webserver, daemon=True);
webserver.start();

window = webview.create_window("Searotes", "http://127.0.0.1:5000");
webview.start(window);
