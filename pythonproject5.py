import sqlite3
import random 
import tkinter as tk
import sqlite3
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#FreeCurrencyAPI key
API_KEY = "fca_live_bStX1hF5ZdIq2wEM0CQzUudy4CwdqK0bUdleidtE"
def create_accno():
    first_digit = random.randint(1, 9)
    
    remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(10))
    
    random_number = str(first_digit) + remaining_digits
    return int(random_number)

def fetch_historical_rates(start_date, end_date, target_currency, base_currency="GBP"):
    rates_list = []
    current_date = start_date

    while current_date <= end_date:
        # Format the date in YYYY-MM-DD
        formatted_date = current_date.strftime("%Y-%m-%d")
        
        # API URL for the specific date (default base currency is EUR)
        url = f"http://data.fixer.io/api/{formatted_date}?access_key={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                rates = data["rates"]
                
                # Calculate GBP to target_currency rate: (target_currency / GBP)
                if base_currency in rates and target_currency in rates:
                    gbp_to_target = rates[target_currency] / rates[base_currency]
                    rates_list.append(gbp_to_target)
                else:
                    print(f"Rate not found for {formatted_date}")
            else:
                print(f"Error on {formatted_date}: {data.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error fetching data for {formatted_date}: {e}")
        
        # Move to the next date
        current_date += timedelta(days=1)

    return rates_list

dbase = sqlite3.connect("bank_data6.db")
cursor = dbase.cursor()
dbase.execute(''' CREATE TABLE IF NOT EXISTS customer(
                accNo INT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                password INT NOT NULL,
                location TEXT NOT NULL,
                balance INT NOT NULL)''')

dbaseMap = {"accno":0,"name":1,"password":2,"location":3,"balance":4}

#--------------------------------------------------
def insert_data(NAME,PASSWORD,LOCATION,BALANCE):
    dbase.execute('''INSERT INTO customer(ACCNO,NAME,PASSWORD,LOCATION,BALANCE)
                    VALUES(?,?,?,?,?)''',(create_accno(),NAME,PASSWORD,LOCATION,BALANCE))
    dbase.commit()

#----------------------------------------------------------------------
def read_data(id,column="ACCNO"):
    # query = f"SELECT * FROM customer WHERE {column} = ?"
    # data = dbase.execute(query,(id,))
    # return data
    query = f"SELECT * FROM customer WHERE {column} = ?"
    cursor = dbase.execute(query, (id,))
    result = cursor.fetchone()  # Fetch the first row of the result
    return result if result else False
#----------------------------------------------------------------------
def update_data(column,value,id):
    query = f"UPDATE customer SET {column} = ? WHERE ACCNO = ?"
    dbase.execute(query, (value, id))
    dbase.commit()
#----------------------------------------------------------------------
def delete_data(id):
    dbase.execute("DELETE FROM customer WHERE ACCNO=?", (id,))

    dbase.commit()
#----------------------------------------------------------------------
def transfer(id1,id2,amount):
    query = "SELECT ACCNO, BALANCE FROM customer WHERE ACCNO = ?"
    data = dbase.execute(query, (id1,))
    record = data.fetchone()
    balance1 = record[1]
    query = "SELECT ACCNO, BALANCE FROM customer WHERE ACCNO = ?"
    data = dbase.execute(query, (id2,))
    record = data.fetchone()
    balance2 = record[1]
    balance1,balance2 = balance1-amount,balance2+amount
    update_data("BALANCE",balance1,id1)
    update_data("BALANCE",balance2,id2)
    dbase.commit()

#----------------------------------------------------------------------

#--------------------------------------------------------

# transfer(10502802774,63096821694,100)
# insert_data("alex","345","brazil","2341")
# update_data("location","hello",12312)
# read_data()
# dbase.commit()



def open_transfer_tab(data):
    # New window for transfer
    transfer_window = tk.Toplevel()
    transfer_window.title("Transfer")
    transfer_window.geometry("300x200")

    # Add input fields
    tk.Label(transfer_window, text="Receiver Account Number:").pack(pady=5)
    receiver_entry = tk.Entry(transfer_window)
    receiver_entry.pack(pady=5)

    tk.Label(transfer_window, text="Amount:").pack(pady=5)
    amount_entry = tk.Entry(transfer_window)
    amount_entry.pack(pady=5)

    def execute_transfer():
        receiver_accno = receiver_entry.get()
        amount = amount_entry.get()

        if not receiver_accno or not amount:
            messagebox.showerror("Transfer Failed", "Please fill in all fields.")
            return

        if not receiver_accno.isdigit():
            messagebox.showerror("Transfer Failed", "Amount must be a valid number.")
            return 
        
        if not amount.isdigit():
            messagebox.showerror("Transfer Failed", "Amount must be a valid number.")
            return

        receiver_accno = int(receiver_accno)
        amount = int(amount)
        # Ensure the receiver account exists
        receiver_data = read_data(receiver_accno)
        if not receiver_data:
            messagebox.showerror("Transfer Failed", "Receiver account does not exist.")
            return

        # Perform the transfer
        transfer(data[dbaseMap["accno"]], receiver_accno, amount)
        transfer_window.destroy()

    # Transfer button
    tk.Button(transfer_window, text="Transfer", command=execute_transfer).pack(pady=10)
    transfer_window.mainloop()


def open_dashboard(data):
    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("300x200")

    # Customer details
    tk.Label(dashboard, text="Customer", font=("Arial", 8, "bold")).place(x=8, y=8)
    tk.Label(dashboard, text=f"AccNo: {data[dbaseMap["name"]]}", font=("Arial", 9)).place(x=10, y=35)

    tk.Button(dashboard, text="Balance", command=lambda: show_balance(data)).pack(pady=5)
    tk.Button(dashboard, text="Transfer", command=lambda: open_transfer_tab(data)).pack(pady=5)
    tk.Button(dashboard, text="Currency", command=show_currency).pack(pady=5)
    tk.Button(dashboard, text="Help", command=show_help).pack(pdy=5)

    dashboard.mainloop()

def login():
    accno = int(accno_entry.get())
    password = int(password_entry.get())
    record = read_data(accno)

    if not record:
        messagebox.showerror("Login Failed", "Account not found.")
        return

    print(record[dbaseMap["password"]])  # This will now only run if record is valid.

    if password == record[dbaseMap["password"]]:
        messagebox.showinfo("Login Successful", record)
        root.destroy()
        open_dashboard(record)
    else:
        messagebox.showerror("Login Failed", "Incorrect password.")

def show_balance(): messagebox.showinfo("Balance", "Your balance is $1,000.")
def show_transfer(): messagebox.showinfo("Transfer", "Transfer feature coming soon.")
def show_currency(): messagebox.showinfo("Currency", "Currency feature coming soon.")
def show_help(): messagebox.showinfo("Help", "For help, contact support@example.com.")

# Login window
root = tk.Tk()
root.title("Login Screen")
root.geometry("300x200")

tk.Label(root, text="Account Number:").pack(pady=5)
accno_entry = tk.Entry(root)
accno_entry.pack(pady=5)

tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

tk.Button(root, text="Login", command=login).pack(pady=10)
root.mainloop()
dbase.close()
