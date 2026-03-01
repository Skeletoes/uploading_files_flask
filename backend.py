import os
from flask import Flask, flash, request, redirect, url_for, render_template, g
from werkzeug.utils import secure_filename
import sqlite3
import sys
from flaskwebgui import FlaskUI


UPLOAD_FOLDER = 'upload_folder'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Handle PyInstaller bundled database path
if getattr(sys, 'frozen', False):
    # Running as a bundled PyInstaller executable
    database_dir = sys._MEIPASS
else:
    # Running as a normal Python script
    database_dir = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(database_dir, 'database.db')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/download/<name>')
def download_file(name):
    return f"File '{name}' downloaded!"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('upload_frontend.html')

if __name__ == '__main__':
    FlaskUI(app=app, server="flask", width=800, height=480, port=8000).run()
    app.run(debug=True)