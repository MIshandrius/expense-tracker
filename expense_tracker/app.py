from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "expenses.db"

## Database connection function to get a connection to the SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

## Database initialization function to create the expenses table if it doesn't exist
def init_db():
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

## Route for the home page that displays the list of expenses, total amount, and category filter
@app.route("/")
def index():
    conn = get_db()

    category_filter = request.args.get("category", "")

    ## Fetch expenses from the database, applying category filter if provided, and calculate the total amount
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

    ## Close the database connection and render the index template with the fetched data
    conn.close()
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=categories,
        selected_category=category_filter
    )

## Route for adding a new expense, handling both GET and POST requests
@app.route("/add", methods=["GET", "POST"])
def add_expense():
    ## If the request method is POST, insert the new expense into the database
    if request.method == "POST":
        title    = request.form["title"].strip()
        amount   = request.form["amount"]
        category = request.form["category"].strip()
        date     = request.form["date"]
        note     = request.form.get("note", "").strip()
        
        ## Validate the input data and return an error message if any required field is missing
        if not title or not amount or not category or not date:
            error = "Please fill in all required fields."
            return render_template("add.html", error=error)

        ## Insert the new expense into the database and redirect to the home page
        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (title, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (title, float(amount), category, date, note)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html")

## Route for editing an existing expense, handling both GET and POST requests
@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):

    ## Fetch the expense with the given ID from the database
    conn = get_db()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()

    ## If the expense with the given ID is not found, return a 404 error
    if expense is None:
        conn.close()
        return "Expense not found", 404
    
    ## If the request method is POST, update the expense with the new data from the form
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

## Route for deleting an expense, handling POST requests
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

## Main block to initialize the database and run the Flask application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
