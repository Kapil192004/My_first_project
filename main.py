import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "library.db"

def db_connect():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL, author TEXT NOT NULL, category TEXT,
        total INTEGER NOT NULL, available INTEGER NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS issues(
        id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER NOT NULL,
        student TEXT NOT NULL, roll TEXT NOT NULL, issue_date TEXT NOT NULL,
        return_date TEXT, status TEXT NOT NULL DEFAULT 'Issued')""")
    con.commit()
    return con

class App:
    def __init__(self, root):
        self.root, self.con, self.selected = root, db_connect(), None
        root.title("Library Management System")
        root.geometry("1050x650")
        root.minsize(850, 540)
        tk.Label(root, text="LIBRARY MANAGEMENT SYSTEM", bg="#263b5a",
                 fg="white", font=("Arial", 20, "bold"), pady=14).pack(fill="x")
        tabs = ttk.Notebook(root)
        self.books_tab, self.issue_tab = ttk.Frame(tabs, padding=12), ttk.Frame(tabs, padding=12)
        tabs.add(self.books_tab, text="Manage Books")
        tabs.add(self.issue_tab, text="Issue / Return")
        tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self.make_books()
        self.make_issues()
        self.refresh_books()
        self.refresh_issues()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def make_books(self):
        f = ttk.LabelFrame(self.books_tab, text="Book Details", padding=10)
        f.pack(fill="x")
        self.bv = {k: tk.StringVar() for k in ("code","title","author","category","total")}
        fields = [("Book Code","code",0,0),("Title","title",0,2),
                  ("Author","author",1,0),("Category","category",1,2),
                  ("Total Copies","total",2,0)]
        for label,key,r,c in fields:
            ttk.Label(f,text=label).grid(row=r,column=c,sticky="w",padx=5,pady=5)
            ttk.Entry(f,textvariable=self.bv[key],width=28).grid(row=r,column=c+1,sticky="ew",padx=5,pady=5)
        for c in range(4): f.columnconfigure(c,weight=1)
        bar=ttk.Frame(f); bar.grid(row=3,column=0,columnspan=4,pady=7)
        for label,cmd in [("Add Book",self.add_book),("Update",self.update_book),
                          ("Delete",self.delete_book),("Clear",self.clear_book)]:
            ttk.Button(bar,text=label,command=cmd).pack(side="left",padx=4)
        s=ttk.Frame(self.books_tab); s.pack(fill="x",pady=9)
        ttk.Label(s,text="Search title / author / code:").pack(side="left")
        self.search=tk.StringVar()
        ttk.Entry(s,textvariable=self.search,width=30).pack(side="left",padx=7)
        ttk.Button(s,text="Search",command=self.search_books).pack(side="left",padx=3)
        ttk.Button(s,text="Show All",command=self.refresh_books).pack(side="left",padx=3)
        frame=ttk.Frame(self.books_tab); frame.pack(fill="both",expand=True)
        cols=("id","code","title","author","category","total","available")
        self.bt=ttk.Treeview(frame,columns=cols,show="headings")
        for c,h,w in zip(cols,("ID","Code","Title","Author","Category","Total","Available"),(45,95,220,160,120,70,85)):
            self.bt.heading(c,text=h); self.bt.column(c,width=w,anchor="center")
        sb=ttk.Scrollbar(frame,orient="vertical",command=self.bt.yview)
        self.bt.configure(yscrollcommand=sb.set)
        self.bt.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self.bt.bind("<<TreeviewSelect>>",self.select_book)

    def make_issues(self):
        f=ttk.LabelFrame(self.issue_tab,text="Issue a Book",padding=10); f.pack(fill="x")
        self.iv={k:tk.StringVar() for k in ("code","student","roll","date")}
        fields=[("Book Code","code",0,0),("Student Name","student",0,2),
                ("Student Roll No.","roll",1,0),("Issue Date (YYYY-MM-DD)","date",1,2)]
        for label,key,r,c in fields:
            ttk.Label(f,text=label).grid(row=r,column=c,sticky="w",padx=5,pady=5)
            ttk.Entry(f,textvariable=self.iv[key],width=28).grid(row=r,column=c+1,sticky="ew",padx=5,pady=5)
        for c in range(4): f.columnconfigure(c,weight=1)
        ttk.Button(f,text="Issue Book",command=self.issue_book).grid(row=2,column=0,columnspan=2,pady=7)
        ttk.Button(f,text="Clear",command=self.clear_issue).grid(row=2,column=2,columnspan=2,pady=7)
        ttk.Label(self.issue_tab,text="Issue History",font=("Arial",12,"bold")).pack(anchor="w",pady=(12,5))
        frame=ttk.Frame(self.issue_tab); frame.pack(fill="both",expand=True)
        cols=("id","title","code","student","roll","date","status")
        self.it=ttk.Treeview(frame,columns=cols,show="headings")
        for c,h,w in zip(cols,("Issue ID","Book Title","Code","Student","Roll No.","Issue Date","Status"),(65,190,90,150,100,110,90)):
            self.it.heading(c,text=h); self.it.column(c,width=w,anchor="center")
        sb=ttk.Scrollbar(frame,orient="vertical",command=self.it.yview)
        self.it.configure(yscrollcommand=sb.set)
        self.it.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        ttk.Button(self.issue_tab,text="Return Selected Book",command=self.return_book).pack(anchor="e",pady=8)

    def add_book(self):
        code,title,author,cat,total=[self.bv[k].get().strip() for k in self.bv]
        if not all((code,title,author,total)):
            messagebox.showwarning("Required","Code, title, author and quantity are required."); return
        try:
            n=int(total)
            if n<1: raise ValueError
            self.con.execute("INSERT INTO books(code,title,author,category,total,available) VALUES(?,?,?,?,?,?)",(code,title,author,cat,n,n))
            self.con.commit(); self.refresh_books(); self.clear_book()
            messagebox.showinfo("Success","Book added.")
        except ValueError: messagebox.showerror("Quantity","Enter a positive whole number.")
        except sqlite3.IntegrityError: messagebox.showerror("Duplicate","Book code already exists.")

    def update_book(self):
        if not self.selected: messagebox.showwarning("Select","Select a book first."); return
        code,title,author,cat,total=[self.bv[k].get().strip() for k in self.bv]
        if not all((code,title,author,total)): messagebox.showwarning("Required","Fill required fields."); return
        try:
            n=int(total)
            old=self.con.execute("SELECT total,available FROM books WHERE id=?",(self.selected,)).fetchone()
            issued=old[0]-old[1]
            if n<1 or n<issued: raise ValueError
            self.con.execute("UPDATE books SET code=?,title=?,author=?,category=?,total=?,available=? WHERE id=?",
                             (code,title,author,cat,n,n-issued,self.selected))
            self.con.commit(); self.refresh_books(); self.clear_book()
        except ValueError: messagebox.showerror("Quantity","Quantity must be positive and not less than copies currently issued.")
        except sqlite3.IntegrityError: messagebox.showerror("Duplicate","Book code already exists.")

    def delete_book(self):
        if not self.selected: messagebox.showwarning("Select","Select a book first."); return
        active=self.con.execute("SELECT COUNT(*) FROM issues WHERE book_id=? AND status='Issued'",(self.selected,)).fetchone()[0]
        if active: messagebox.showerror("Cannot delete","Return issued copies before deleting this book."); return
        if messagebox.askyesno("Confirm","Delete selected book?"):
            self.con.execute("DELETE FROM books WHERE id=?",(self.selected,)); self.con.commit()
            self.refresh_books(); self.clear_book()

    def select_book(self,event=None):
        sel=self.bt.selection()
        if not sel:return
        row=self.bt.item(sel[0],"values"); self.selected=int(row[0])
        for k,v in zip(self.bv,(row[1],row[2],row[3],row[4],row[5])): self.bv[k].set(v)

    def clear_book(self):
        for v in self.bv.values():v.set("")
        self.selected=None
        self.bt.selection_remove(self.bt.selection())

    def show_books(self,rows):
        for x in self.bt.get_children():self.bt.delete(x)
        for row in rows:self.bt.insert("","end",values=row)

    def refresh_books(self):
        self.search.set("")
        self.show_books(self.con.execute("SELECT id,code,title,author,category,total,available FROM books ORDER BY title").fetchall())

    def search_books(self):
        q="%"+self.search.get().strip()+"%"
        rows=self.con.execute("""SELECT id,code,title,author,category,total,available FROM books
          WHERE code LIKE ? OR title LIKE ? OR author LIKE ? ORDER BY title""",(q,q,q)).fetchall()
        self.show_books(rows)

    def issue_book(self):
        code,name,roll,date=[self.iv[k].get().strip() for k in self.iv]
        if not all((code,name,roll,date)):messagebox.showwarning("Required","Fill all issue details.");return
        book=self.con.execute("SELECT id,available FROM books WHERE code=?",(code,)).fetchone()
        if not book:messagebox.showerror("Not found","Book code not found.");return
        if book[1]<1:messagebox.showerror("Unavailable","No available copy.");return
        self.con.execute("INSERT INTO issues(book_id,student,roll,issue_date,status) VALUES(?,?,?,?, 'Issued')",(book[0],name,roll,date))
        self.con.execute("UPDATE books SET available=available-1 WHERE id=?",(book[0],))
        self.con.commit();self.refresh_books();self.refresh_issues();self.clear_issue()
        messagebox.showinfo("Success","Book issued.")

    def return_book(self):
        sel=self.it.selection()
        if not sel:messagebox.showwarning("Select","Select an issue record.");return
        issue_id=int(self.it.item(sel[0],"values")[0])
        row=self.con.execute("SELECT book_id,status FROM issues WHERE id=?",(issue_id,)).fetchone()
        if not row or row[1]!="Issued":messagebox.showinfo("Returned","This book is already returned.");return
        self.con.execute("UPDATE issues SET status='Returned',return_date=date('now') WHERE id=?",(issue_id,))
        self.con.execute("UPDATE books SET available=available+1 WHERE id=?",(row[0],))
        self.con.commit();self.refresh_books();self.refresh_issues()
        messagebox.showinfo("Success","Book returned.")

    def refresh_issues(self):
        rows=self.con.execute("""SELECT i.id,b.title,b.code,i.student,i.roll,i.issue_date,i.status
          FROM issues i JOIN books b ON b.id=i.book_id ORDER BY i.id DESC""").fetchall()
        for x in self.it.get_children():self.it.delete(x)
        for row in rows:self.it.insert("","end",values=row)

    def clear_issue(self):
        for v in self.iv.values():v.set("")

    def close(self):
        self.con.close();self.root.destroy()

if __name__=="__main__":
    root=tk.Tk(); app=App(root); root.mainloop()
