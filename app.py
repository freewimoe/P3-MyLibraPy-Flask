from flask import Flask, render_template, request, redirect, send_file
import json
import os
import csv

app = Flask(__name__)
DATA_FILE = "books.json"  # File that stores the book list in JSON format


# ---------- HELPER FUNCTIONS ----------

def load_books():
    # Try reading the JSON file, return a list of books or an empty list
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Could not read {DATA_FILE}: {e}")
    return []  # If file doesn't exist or fails, return empty list

def save_books(books):
    # Save the book list back to the JSON file
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(books, f, indent=4)
    except Exception as e:
        print(f"[Error] Could not write to {DATA_FILE}: {e}")

def export_books_to_csv(books, filename="books_export.csv"):
    # Export books into a CSV file with headers title, author, genre, status
    if not books:
        return False  # No data to export
    try:
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["title", "author", "genre", "status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # Write CSV header
            for book in books:
                writer.writerow(book)  # Write each book as row
        return True
    except Exception as e:
        print(f"[Error] Export failed: {e}")
        return False


# ---------- ROUTES (the endpoints Flask listens to) ----------

@app.route("/", methods=["GET", "POST"])
def index():
    # Home route: either shows list or processes form to add a new book
    books = load_books()

    if request.method == "POST":
        # Extract submitted data from form fields
        title = request.form["title"]
        author = request.form["author"]
        genre = request.form.get("genre", "")
        status = request.form.get("status", "")

        # Create a new book entry as dictionary
        new_book = {
            "title": title.strip(),
            "author": author.strip(),
            "genre": genre.strip(),
            "status": status.strip()
        }

        books.append(new_book)  # Add book to in-memory list
        save_books(books)  # Persist to JSON
        return redirect("/")  # Reload the page to update the list

    return render_template("index.html", books=books)  # Show current state


@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit(book_id):
    # Edit an existing book by index (book_id)
    books = load_books()

    if not (0 <= book_id < len(books)):
        return "Book not found", 404  # Out-of-range check

    if request.method == "POST":
        # Update the fields of the selected book
        books[book_id]["title"] = request.form["title"]
        books[book_id]["author"] = request.form["author"]
        books[book_id]["genre"] = request.form.get("genre", "")
        books[book_id]["status"] = request.form.get("status", "")
        save_books(books)
        return redirect("/")

    book = books[book_id]  # Get the book object to prefill the form
    return render_template("edit.html", book=book, book_id=book_id)


@app.route("/delete/<int:book_id>")
def delete(book_id):
    # Remove a book from the list by ID
    books = load_books()

    if not (0 <= book_id < len(books)):
        return "Book not found", 404

    books.pop(book_id)  # Delete the book from list
    save_books(books)  # Save updated list
    return redirect("/")


@app.route("/export")
def export():
    # Trigger export and download CSV version of the book list
    books = load_books()
    filename = "books_export.csv"

    if export_books_to_csv(books, filename):
        return send_file(filename, as_attachment=True)
    return "Export failed", 500


# ---------- MAIN ENTRY POINT ----------

if __name__ == "__main__":
    # Run app locally or on Heroku (picks $PORT env var if deployed)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
