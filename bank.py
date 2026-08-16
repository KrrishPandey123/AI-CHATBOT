import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import random

# ================= DATABASE =================

conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    account_no INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    pin TEXT NOT NULL,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no INTEGER,
    type TEXT,
    amount REAL,
    date TEXT
)
""")

conn.commit()


# ================= MAIN APPLICATION =================

class BankManagementSystem:

    def __init__(self, root):
        self.root = root
        self.root.title("Bank Management System")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.current_account = None

        self.login_screen()

    # ================= CLEAR SCREEN =================

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ================= LOGIN SCREEN =================

    def login_screen(self):
        self.clear_screen()

        title = tk.Label(
            self.root,
            text="BANK MANAGEMENT SYSTEM",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=30)

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        tk.Label(frame, text="Account Number",
                 font=("Arial", 12)).grid(row=0, column=0, pady=10)

        self.account_entry = tk.Entry(frame, width=30)
        self.account_entry.grid(row=0, column=1, pady=10)

        tk.Label(frame, text="PIN",
                 font=("Arial", 12)).grid(row=1, column=0, pady=10)

        self.pin_entry = tk.Entry(frame, width=30, show="*")
        self.pin_entry.grid(row=1, column=1, pady=10)

        tk.Button(
            self.root,
            text="Login",
            width=20,
            command=self.login
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Create New Account",
            width=20,
            command=self.create_account_screen
        ).pack(pady=10)

    # ================= CREATE ACCOUNT =================

    def create_account_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="CREATE NEW ACCOUNT",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(frame, text="Name").grid(row=0, column=0, pady=10)
        self.name_entry = tk.Entry(frame, width=30)
        self.name_entry.grid(row=0, column=1)

        tk.Label(frame, text="Phone").grid(row=1, column=0, pady=10)
        self.phone_entry = tk.Entry(frame, width=30)
        self.phone_entry.grid(row=1, column=1)

        tk.Label(frame, text="PIN").grid(row=2, column=0, pady=10)
        self.new_pin_entry = tk.Entry(frame, width=30, show="*")
        self.new_pin_entry.grid(row=2, column=1)

        tk.Label(frame, text="Initial Deposit").grid(row=3, column=0, pady=10)
        self.deposit_entry = tk.Entry(frame, width=30)
        self.deposit_entry.grid(row=3, column=1)

        tk.Button(
            self.root,
            text="Create Account",
            width=20,
            command=self.create_account
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Back to Login",
            width=20,
            command=self.login_screen
        ).pack()

    def create_account(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        pin = self.new_pin_entry.get().strip()
        deposit = self.deposit_entry.get().strip()

        if not name or not phone or not pin or not deposit:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if not pin.isdigit() or len(pin) != 4:
            messagebox.showerror("Error", "PIN must contain exactly 4 digits.")
            return

        try:
            deposit = float(deposit)

            if deposit < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Enter a valid deposit amount.")
            return

        account_no = random.randint(10000000, 99999999)

        cursor.execute(
            "INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
            (account_no, name, phone, pin, deposit)
        )

        if deposit > 0:
            cursor.execute(
                """INSERT INTO transactions
                   (account_no, type, amount, date)
                   VALUES (?, ?, ?, ?)""",
                (
                    account_no,
                    "Initial Deposit",
                    deposit,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

        conn.commit()

        messagebox.showinfo(
            "Account Created",
            f"Account created successfully!\n\n"
            f"Account Number: {account_no}\n"
            f"Name: {name}"
        )

        self.login_screen()

    # ================= LOGIN =================

    def login(self):
        account_no = self.account_entry.get().strip()
        pin = self.pin_entry.get().strip()

        if not account_no or not pin:
            messagebox.showerror("Error", "Enter account number and PIN.")
            return

        cursor.execute(
            "SELECT * FROM accounts WHERE account_no=? AND pin=?",
            (account_no, pin)
        )

        account = cursor.fetchone()

        if account:
            self.current_account = int(account_no)
            self.dashboard()
        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid account number or PIN."
            )

    # ================= DASHBOARD =================

    def dashboard(self):
        self.clear_screen()

        cursor.execute(
            "SELECT name, balance FROM accounts WHERE account_no=?",
            (self.current_account,)
        )

        account = cursor.fetchone()

        tk.Label(
            self.root,
            text="BANK DASHBOARD",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        tk.Label(
            self.root,
            text=f"Welcome, {account[0]}",
            font=("Arial", 16)
        ).pack(pady=5)

        tk.Label(
            self.root,
            text=f"Account Number: {self.current_account}",
            font=("Arial", 12)
        ).pack(pady=5)

        tk.Label(
            self.root,
            text=f"Balance: ₹{account[1]:.2f}",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        buttons = [
            ("Deposit Money", self.deposit_screen),
            ("Withdraw Money", self.withdraw_screen),
            ("Transfer Money", self.transfer_screen),
            ("Transaction History", self.transaction_history),
            ("Change PIN", self.change_pin_screen),
            ("Logout", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            tk.Button(
                frame,
                text=text,
                width=22,
                height=2,
                command=command
            ).grid(
                row=i // 2,
                column=i % 2,
                padx=10,
                pady=8
            )

    # ================= DEPOSIT =================

    def deposit_screen(self):
        self.amount_window("Deposit Money", self.deposit)

    def deposit(self, amount, window):
        if amount <= 0:
            messagebox.showerror("Error", "Enter a valid amount.")
            return

        cursor.execute(
            "UPDATE accounts SET balance=balance+? WHERE account_no=?",
            (amount, self.current_account)
        )

        cursor.execute(
            """INSERT INTO transactions
               (account_no, type, amount, date)
               VALUES (?, ?, ?, ?)""",
            (
                self.current_account,
                "Deposit",
                amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()

        window.destroy()

        messagebox.showinfo(
            "Success",
            f"₹{amount:.2f} deposited successfully."
        )

        self.dashboard()

    # ================= WITHDRAW =================

    def withdraw_screen(self):
        self.amount_window("Withdraw Money", self.withdraw)

    def withdraw(self, amount, window):
        if amount <= 0:
            messagebox.showerror("Error", "Enter a valid amount.")
            return

        cursor.execute(
            "SELECT balance FROM accounts WHERE account_no=?",
            (self.current_account,)
        )

        balance = cursor.fetchone()[0]

        if amount > balance:
            messagebox.showerror(
                "Error",
                "Insufficient balance."
            )
            return

        cursor.execute(
            "UPDATE accounts SET balance=balance-? WHERE account_no=?",
            (amount, self.current_account)
        )

        cursor.execute(
            """INSERT INTO transactions
               (account_no, type, amount, date)
               VALUES (?, ?, ?, ?)""",
            (
                self.current_account,
                "Withdrawal",
                amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()

        window.destroy()

        messagebox.showinfo(
            "Success",
            f"₹{amount:.2f} withdrawn successfully."
        )

        self.dashboard()

    # ================= AMOUNT WINDOW =================

    def amount_window(self, title, function):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("350x180")
        window.resizable(False, False)

        tk.Label(
            window,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(
            window,
            text="Enter Amount:"
        ).pack()

        amount_entry = tk.Entry(window, width=25)
        amount_entry.pack(pady=10)

        def submit():
            try:
                amount = float(amount_entry.get())
                function(amount, window)
            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Please enter a valid amount."
                )

        tk.Button(
            window,
            text="Submit",
            width=15,
            command=submit
        ).pack()

    # ================= TRANSFER =================

    def transfer_screen(self):
        window = tk.Toplevel(self.root)
        window.title("Transfer Money")
        window.geometry("400x300")
        window.resizable(False, False)

        tk.Label(
            window,
            text="TRANSFER MONEY",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(window, text="Receiver Account Number").pack()

        receiver_entry = tk.Entry(window, width=30)
        receiver_entry.pack(pady=10)

        tk.Label(window, text="Amount").pack()

        amount_entry = tk.Entry(window, width=30)
        amount_entry.pack(pady=10)

        def transfer():
            receiver = receiver_entry.get().strip()

            try:
                amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid amount.")
                return

            if amount <= 0:
                messagebox.showerror("Error", "Invalid amount.")
                return

            if receiver == str(self.current_account):
                messagebox.showerror(
                    "Error",
                    "You cannot transfer to your own account."
                )
                return

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=?",
                (self.current_account,)
            )

            sender = cursor.fetchone()

            cursor.execute(
                "SELECT account_no FROM accounts WHERE account_no=?",
                (receiver,)
            )

            receiver_exists = cursor.fetchone()

            if not receiver_exists:
                messagebox.showerror(
                    "Error",
                    "Receiver account not found."
                )
                return

            if amount > sender[0]:
                messagebox.showerror(
                    "Error",
                    "Insufficient balance."
                )
                return

            cursor.execute(
                "UPDATE accounts SET balance=balance-? WHERE account_no=?",
                (amount, self.current_account)
            )

            cursor.execute(
                "UPDATE accounts SET balance=balance+? WHERE account_no=?",
                (amount, receiver)
            )

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """INSERT INTO transactions
                   (account_no, type, amount, date)
                   VALUES (?, ?, ?, ?)""",
                (
                    self.current_account,
                    f"Transfer to {receiver}",
                    amount,
                    date
                )
            )

            cursor.execute(
                """INSERT INTO transactions
                   (account_no, type, amount, date)
                   VALUES (?, ?, ?, ?)""",
                (
                    receiver,
                    f"Transfer from {self.current_account}",
                    amount,
                    date
                )
            )

            conn.commit()

            window.destroy()

            messagebox.showinfo(
                "Success",
                f"₹{amount:.2f} transferred successfully."
            )

            self.dashboard()

        tk.Button(
            window,
            text="Transfer",
            width=18,
            command=transfer
        ).pack(pady=15)

    # ================= TRANSACTION HISTORY =================

    def transaction_history(self):
        window = tk.Toplevel(self.root)
        window.title("Transaction History")
        window.geometry("650x400")

        tk.Label(
            window,
            text="TRANSACTION HISTORY",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        columns = ("ID", "Type", "Amount", "Date")

        tree = ttk.Treeview(
            window,
            columns=columns,
            show="headings"
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        cursor.execute(
            """SELECT id, type, amount, date
               FROM transactions
               WHERE account_no=?
               ORDER BY id DESC""",
            (self.current_account,)
        )

        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"₹{row[2]:.2f}",
                row[3]
            ))

    # ================= CHANGE PIN =================

    def change_pin_screen(self):
        window = tk.Toplevel(self.root)
        window.title("Change PIN")
        window.geometry("350x250")

        tk.Label(
            window,
            text="CHANGE PIN",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        tk.Label(window, text="Old PIN").pack()

        old_pin = tk.Entry(window, show="*", width=25)
        old_pin.pack(pady=5)

        tk.Label(window, text="New PIN").pack()

        new_pin = tk.Entry(window, show="*", width=25)
        new_pin.pack(pady=5)

        def change():
            cursor.execute(
                "SELECT pin FROM accounts WHERE account_no=?",
                (self.current_account,)
            )

            current_pin = cursor.fetchone()[0]

            if old_pin.get() != current_pin:
                messagebox.showerror(
                    "Error",
                    "Old PIN is incorrect."
                )
                return

            if not new_pin.get().isdigit() or len(new_pin.get()) != 4:
                messagebox.showerror(
                    "Error",
                    "New PIN must contain exactly 4 digits."
                )
                return

            cursor.execute(
                "UPDATE accounts SET pin=? WHERE account_no=?",
                (new_pin.get(), self.current_account)
            )

            conn.commit()

            window.destroy()

            messagebox.showinfo(
                "Success",
                "PIN changed successfully."
            )

        tk.Button(
            window,
            text="Change PIN",
            width=18,
            command=change
        ).pack(pady=15)

    # ================= LOGOUT =================

    def logout(self):
        self.current_account = None
        self.login_screen()


# ================= RUN APPLICATION =================

root = tk.Tk()
app = BankManagementSystem(root)

root.mainloop()

conn.close()
