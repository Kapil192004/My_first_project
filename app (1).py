import sqlite3
from pathlib import Path
from datetime import date
import streamlit as st

DB = Path(__file__).with_name("library.db")

def connect():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL,
        category TEXT, total INTEGER NOT NULL, available INTEGER NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS issues(
        id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL,
        student TEXT NOT NULL, roll TEXT NOT NULL, issue_date TEXT NOT NULL,
        return_date TEXT, status TEXT NOT NULL DEFAULT 'Issued')""")
    con.commit()
    return con

con = connect()
st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")
st.title("📚 Library Management System")
st.caption("Manage books, issue books to students, and record returns.")

tab1, tab2, tab3 = st.tabs(["Manage Books", "Issue / Return", "Issue History"])

with tab1:
    st.subheader("Add a book")
    with st.form("add_book", clear_on_submit=True):
        c1, c2 = st.columns(2)
        code = c1.text_input("Book code *")
        title = c2.text_input("Book title *")
        author = c1.text_input("Author *")
        category = c2.text_input("Category")
        total = c1.number_input("Total copies *", min_value=1, step=1)
        submitted = st.form_submit_button("Add book", type="primary")
        if submitted:
            if not code.strip() or not title.strip() or not author.strip():
                st.error("Book code, title and author are required.")
            else:
                try:
                    con.execute("INSERT INTO books(code,title,author,category,total,available) VALUES(?,?,?,?,?,?)",
                                (code.strip(), title.strip(), author.strip(), category.strip(), int(total), int(total)))
                    con.commit()
                    st.success("Book added successfully.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That book code already exists.")

    st.subheader("Book catalogue")
    search = st.text_input("Search by code, title or author")
    rows = con.execute("""SELECT * FROM books
        WHERE code LIKE ? OR title LIKE ? OR author LIKE ? ORDER BY title""",
        tuple([f"%{search}%"] * 3)).fetchall()
    if rows:
        st.dataframe([dict(r) for r in rows], use_container_width=True, hide_index=True)
        choices = {f'{r["code"]} — {r["title"]} (ID {r["id"]})': r["id"] for r in rows}
        selected_label = st.selectbox("Select a book to delete", [""] + list(choices))
        if selected_label and st.button("Delete selected book"):
            book_id = choices[selected_label]
            active = con.execute("SELECT COUNT(*) FROM issues WHERE book_id=? AND status='Issued'",
                                 (book_id,)).fetchone()[0]
            if active:
                st.error("Cannot delete: this book has an active issue.")
            else:
                con.execute("DELETE FROM books WHERE id=?", (book_id,))
                con.commit()
                st.success("Book deleted.")
                st.rerun()
    else:
        st.info("No books found. Add your first book above.")

with tab2:
    st.subheader("Issue a book")
    available = con.execute("SELECT * FROM books WHERE available > 0 ORDER BY title").fetchall()
    if available:
        options = {f'{r["code"]} — {r["title"]} (Available: {r["available"]})': r["id"]
                   for r in available}
        with st.form("issue_book", clear_on_submit=True):
            book_label = st.selectbox("Book", list(options))
            student = st.text_input("Student name")
            roll = st.text_input("Student roll number")
            issue_date = st.date_input("Issue date", value=date.today())
            issue_submit = st.form_submit_button("Issue book", type="primary")
            if issue_submit:
                if not student.strip() or not roll.strip():
                    st.error("Enter student name and roll number.")
                else:
                    book_id = options[book_label]
                    con.execute("INSERT INTO issues(book_id,student,roll,issue_date,status) VALUES(?,?,?,?, 'Issued')",
                                (book_id, student.strip(), roll.strip(), issue_date.isoformat()))
                    con.execute("UPDATE books SET available=available-1 WHERE id=? AND available>0",
                                (book_id,))
                    con.commit()
                    st.success("Book issued successfully.")
                    st.rerun()
    else:
        st.info("No available books. Add books in the Manage Books tab.")

    st.subheader("Return a book")
    active = con.execute("""SELECT issues.id, books.title, books.code, issues.student, issues.roll,
        issues.issue_date FROM issues JOIN books ON books.id=issues.book_id
        WHERE issues.status='Issued' ORDER BY issues.issue_date""").fetchall()
    if active:
        return_options = {f'Issue #{r["id"]}: {r["title"]} — {r["student"]} ({r["roll"]})': r["id"]
                          for r in active}
        chosen = st.selectbox("Select active issue", list(return_options))
        if st.button("Return selected book"):
            issue_id = return_options[chosen]
            book_id = con.execute("SELECT book_id FROM issues WHERE id=?",
                                  (issue_id,)).fetchone()["book_id"]
            con.execute("UPDATE issues SET status='Returned', return_date=? WHERE id=?",
                        (date.today().isoformat(), issue_id))
            con.execute("UPDATE books SET available=available+1 WHERE id=?", (book_id,))
            con.commit()
            st.success("Book returned successfully.")
            st.rerun()
    else:
        st.info("There are no books currently issued.")

with tab3:
    st.subheader("Issue history")
    history = con.execute("""SELECT issues.id AS issue_id, books.title, books.code,
        issues.student, issues.roll, issues.issue_date, issues.return_date, issues.status
        FROM issues JOIN books ON books.id=issues.book_id ORDER BY issues.id DESC""").fetchall()
    if history:
        st.dataframe([dict(r) for r in history], use_container_width=True, hide_index=True)
    else:
        st.info("No issue history yet.")

st.divider()
st.caption("Library Management System • Python + Streamlit + SQLite")
