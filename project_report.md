# LIBRARY MANAGEMENT SYSTEM
## BCA Final Year Project Report

**Submitted by:** ____________________  
**Roll Number:** ____________________  
**College:** ____________________  
**Session:** ____________________  
**Project Guide:** ____________________

## 1. Introduction
The Library Management System is a desktop application for maintaining book records and tracking books issued to students.

## 2. Objectives
- Store book information in a database.
- Search books by code, title or author.
- Track total and available copies.
- Record book issue and return transactions.
- Reduce manual record-keeping.

## 3. Scope
This is a local, single-computer prototype for a small library. It manages book details and basic issue/return transactions.

## 4. Technologies
Python 3, Tkinter GUI, SQLite database and Python sqlite3 module.

## 5. Requirements
Computer with 2 GB RAM or more; Windows/Linux/macOS; Python 3.8+; Tkinter.

## 6. Modules
1. Book Management: add, update, delete and view books.
2. Search: search by book code, title or author.
3. Issue Book: assign an available copy to a student.
4. Return Book: mark a loan returned and restore availability.
5. Database: store books and issue transactions.

## 7. Database Design

### books table
| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Unique ID |
| code | TEXT UNIQUE | Book code |
| title | TEXT | Book title |
| author | TEXT | Author |
| category | TEXT | Category |
| total | INTEGER | Total copies |
| available | INTEGER | Available copies |

### issues table
| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Transaction ID |
| book_id | INTEGER | Related book |
| student | TEXT | Student name |
| roll | TEXT | Student roll number |
| issue_date | TEXT | Entered issue date |
| return_date | TEXT | Return date |
| status | TEXT | Issued / Returned |

## 8. Workflow
Open the application, add books, enter a book code and student details to issue a copy, and select an issued transaction to return it. Available quantity decreases on issue and increases on return.

## 9. Testing
| Test | Action | Expected Result |
|---|---|---|
| Add book | Enter valid details | Book is saved |
| Duplicate code | Reuse a code | Duplicate warning |
| Search | Enter title or author | Matching books appear |
| Issue | Issue an available copy | Availability decreases |
| No stock | Issue when none available | Unavailable warning |
| Return | Return an issued book | Status changes and availability increases |
| Delete active loan | Delete book with issued copy | Deletion blocked |

## 10. Advantages
Simple interface, offline use, no separate database server, automatic copy tracking and no third-party Python packages.

## 11. Limitations
Single-computer app; no login or multi-user support; issue date is entered manually; no fine calculation or barcode support.

## 12. Future Enhancements
Login, due dates and fines, barcode scanning, PDF/Excel reports and a web-based multi-user version.

## 13. Conclusion
The project demonstrates how Python GUI programming and SQLite can manage a small library's book collection and lending transactions.

## 14. Bibliography
- https://docs.python.org/3/
- https://docs.python.org/3/library/tkinter.html
- https://www.sqlite.org/docs.html

**Submission reminder:** Add your own details, application screenshots and actual testing results. Follow your college's required report format.
