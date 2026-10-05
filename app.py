import os, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "s"
os.makedirs("uploads", exist_ok=True)

def load(): return json.load(open("apps.json", encoding="utf-8")) if os.path.exists("apps.json") else []
def save(d): json.dump(d, open("apps.json", "w", encoding="utf-8"), ensure_ascii=False)

@app.route("/")
def index(): return render_template("index.html", apps=load())

@app.route("/upload", methods=["POST"])
def upload():
    f, name = request.files.get("apk"), request.form.get("name", "").strip()
    if not f or not name: return redirect("/")
    fn = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(f.filename)
    f.save(os.path.join("uploads", fn))
    a = load()
    a.insert(0, {"id": len(a) + 1, "name": name, "desc": request.form.get("desc", ""),
                 "ver": request.form.get("ver", "1.0"), "file": fn,
                 "size": round(os.path.getsize("uploads/" + fn) / 1048576, 2), "dl": 0})
    save(a)
    return redirect("/")

@app.route("/download/<int:i>")
def download(i):
    a = load()
    x = next((x for x in a if x["id"] == i), None)
    if not x: return "404", 404
    x["dl"] += 1; save(a)
    return send_from_directory("uploads", x["file"], as_attachment=True, download_name=x["name"] + ".apk")

@app.route("/delete/<int:i>", methods=["POST"])
def delete(i):
    a = load()
    x = next((x for x in a if x["id"] == i), None)
    if x:
        p = "uploads/" + x["file"]
        if os.path.exists(p): os.remove(p)
        a.remove(x); save(a)
    return redirect("/")

app.run(debug=True)
