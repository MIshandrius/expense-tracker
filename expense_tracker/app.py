from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Create the Flask app
app = Flask(__name__)

# Database file name
DATABASE = "expenses.db"

# Helper functions to manage the database connection and initialization
def get_db():
    """Connect to the SQLite database and return the connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Makes rows behave like dictionaries
    return conn

# Initialize the database and create the expenses table if it doesn't exist
def init_db():
    """Create the expenses table if it doesn't already exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


# READ - show all expenses
@app.route("/")
def index():
    """Home page: display all expenses and total spending."""
    conn = get_db()

    category_filter = request.args.get("category", "")
# If a category filter is applied, fetch only expenses from that category; otherwise, fetch all expenses. Then calculate the total amount and get the list of unique categories for the filter dropdown. Finally, render the index.html template with the expenses, total, categories, and selected category.
    if category_filter:
        expenses = conn.execute(
            "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC",
            (category_filter,)
        ).fetchall()
    else:
        expenses = conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC"
        ).fetchall()

    total = sum(e["amount"] for e in expenses)

    categories = conn.execute(
        "SELECT DISTINCT category FROM expenses ORDER BY category"
    ).fetchall()

    conn.close()
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        selected_category=category_filter
    )


# CREATE - show form + handle submission
@app.route("/add", methods=["GET", "POST"])
def add_expense():
    """Show the add-expense form (GET) and save a new expense (POST)."""
    if request.method == "POST":
        title    = request.form["title"].strip()
        amount   = request.form["amount"]
        category = request.form["category"].strip()
        date     = request.form["date"]
        note     = request.form.get("note", "").strip()
# Validate that all required fields are filled in; if not, show an error message. If validation passes, insert the new expense into the database and redirect to the home page.
        if not title or not amount or not category or not date:
            error = "Please fill in all required fields."
            return render_template("add.html", error=error)

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (title, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (title, float(amount), category, date, note)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html")


# UPDATE - show pre-filled form + handle changes
@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    """Show the edit form for an existing expense and save changes."""
    conn = get_db()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
# If the expense with the given ID does not exist, return a 404 error. If the form is submitted (POST), update the expense in the database with the new values and redirect to the home page. If it's a GET request, render the edit.html template with the existing expense data pre-filled in the form.
    if expense is None:
        conn.close()
        return "Expense not found", 404
# If the form is submitted (POST), update the expense in the database with the new values and redirect to the home page. If it's a GET request, render the edit.html template with the existing expense data pre-filled in the form.
    if request.method == "POST":
        title    = request.form["title"].strip()
        amount   = request.form["amount"]
        category = request.form["category"].strip()
        date     = request.form["date"]
        note     = request.form.get("note", "").strip()

        conn.execute(
            """UPDATE expenses
               SET title = ?, amount = ?, category = ?, date = ?, note = ?
               WHERE id = ?""",
            (title, float(amount), category, date, note, expense_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", expense=expense)


# DELETE - remove an expense
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    """Delete an expense by its ID."""
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# Run the app
if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))  # Railway sets PORT automatically
    app.run(host="0.0.0.0", port=port, debug=False)
