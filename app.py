from flask import Flask, render_template, request, redirect, send_file
import json
import os
import csv

app = Flask(__name__)
DATA_FILE = "books.json"


# ---------- UTILITY FUNCTIONS ----------

def load_books():
    """Load book list from JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Could not read {DATA_FILE}: {e}")
    return []


def save_books(books):
    """Save book list to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(books, f, indent=4)
    except Exception as e:
        print(f"[Error] Could not write to {DATA_FILE}: {e}")


def export_books_to_csv(books, filename="books_export.csv"):
    """Export book list to CSV file."""
    if not books:
        return False
    try:
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["title", "author", "genre", "status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in books:
                writer.writerow(book)
        return True
    except Exception as e:
        print(f"[Error] Export failed: {e}")
        return False


# ---------- ROUTES ----------

@app.route("/", methods=["GET", "POST"])
def index():
    """Main page: view and add books."""
    books = load_books()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form.get("genre", "")
        status = request.form.get("status", "")

        new_book = {
            "title": title.strip(),
            "author": author.strip(),
            "genre": genre.strip(),
            "status": status.strip()
        }

        books.append(new_book)
        save_books(books)
        return redirect("/")

    return render_template("index.html", books=books)


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit(book_id):
    """Edit an existing book."""
    books = load_books()

    if not (0 <= book_id < len(books)):
        return "Book not found", 404

    if request.method == "POST":
        books[book_id]["title"] = request.form["title"]
        books[book_id]["author"] = request.form["author"]
        books[book_id]["genre"] = request.form.get("genre", "")
        books[book_id]["status"] = request.form.get("status", "")
        save_books(books)
        return redirect("/")

    book = books[book_id]
    return render_template("edit.html", book=book, book_id=book_id)


@app.route("/delete/<int:book_id>")
def delete(book_id):
    """Delete a book."""
    books = load_books()

    if not (0 <= book_id < len(books)):
        return "Book not found", 404

    books.pop(book_id)
    save_books(books)
    return redirect("/")


@app.route("/export")
def export():
    """Export books as CSV file."""
    books = load_books()
    filename = "books_export.csv"

    if export_books_to_csv(books, filename):
        return send_file(filename, as_attachment=True)
    return "Export failed", 500


# ---------- MAIN ----------

if __name__ == "__main__":
    app.run(debug=True)
