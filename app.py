from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = "books.json"

def load_books():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_books(books):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    books = load_books()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        new_book = {"title": title, "author": author}
        books.append(new_book)
        save_books(books)
        return redirect("/")

    return render_template("index.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)
