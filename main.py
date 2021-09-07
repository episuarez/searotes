import os
import webbrowser

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from core import Core

app = Flask(__name__);
core = Core();

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024;
app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.docx', '.pptx'];
app.config['UPLOAD_PATH'] = 'uploads';

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH']);

@app.route("/")
def index():
    results = [];

    if request.args.get("search") != None and request.args.get("search") != "" and len(request.args.get("search")) > 2:
        text = request.args.get("search");
        results = core.search(text);

        return render_template("index.html", text=text, check=core.check, documents_search=results[0], index_time=results[1], search_time=results[2]);
    else:
        results = "";
        return render_template("index.html", check=core.check);

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file'];
    filename = secure_filename(uploaded_file.filename);

    if filename != '':
        file_ext = os.path.splitext(filename)[1]

        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return ("Documento no valido", 400)

        path = os.path.join(app.config['UPLOAD_PATH'], filename);
        uploaded_file.save(path);

    core.index_documents(filename, path);
    os.remove(path);

    return '', 204

@app.route("/checks", methods=["POST"])
def checks():
    core.check = request.json;
    return "", 200

@app.errorhandler(413)
def too_large():
    return ("Fichero demasiado grande", 413);

if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:5000");
    app.run();
