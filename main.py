import sqlite3
import random 
import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

#FreeCurrencyAPI key
API_KEY = "fca_live_bStX1hF5ZdIq2wEM0CQzUudy4CwdqK0bUdleidtE"

#sort customers base of their balance
def bubble_sort(customers):
    n = len(customers)
    #nested for loop for sorting customers
    for i in range(n):
        for j in range(0, n-i-1):
            if customers[j][dbaseMap["balance"]] < customers[j+1][dbaseMap["balance"]]:
                customers[j], customers[j+1] = customers[j+1], customers[j]
    return customers

#create a new tab for show sorted customers data
def display_sorted_data():
    #create new tab for showe costumers
    sorted_data_window = tk.Toplevel()
    sorted_data_window.title("Richest customers") 
    sorted_data_window.geometry("400x400") 

    # fetch customer information
    cursor = dbase.execute("SELECT * FROM customer")
    customers = cursor.fetchall()

    #assign sorted customers
    sorted_customers = bubble_sort(customers)

    tk.Label(sorted_data_window, text="Sorted Customers by Balance", font=("Arial", 14, "bold")).pack(pady=10)

    data_frame = tk.Frame(sorted_data_window)
    data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    headers = ["Name", "Location", "Balance"]
    #create a table heading for showing customers
    for i, header in enumerate(headers):
        tk.Label(data_frame, text=header, font=("Arial", 10, "bold"), relief=tk.GROOVE, width=15).grid(row=0, column=i)
    #write table rows
    for row_index, customer in enumerate(sorted_customers, start=1):
        values = [customer[1], customer[3], customer[4]]
        for col_index, value in enumerate(values):
            tk.Label(data_frame, text=value, font=("Arial", 10), relief=tk.RIDGE, width=15).grid(row=row_index, column=col_index)

    tk.Button(sorted_data_window, text="Close", command=sorted_data_window.destroy).pack(pady=10)

#function for open register tab
def open_register_tab():
    #create new tab for register
    register_window = tk.Toplevel()
    register_window.title("Register New Account") 
    register_window.geometry("300x300") 

    # create boxs for take input
    tk.Label(register_window, text="Name:").pack(pady=5)
    name_entry = tk.Entry(register_window)
    name_entry.pack(pady=5)

    tk.Label(register_window, text="Password (6 digits):").pack(pady=5)
    password_entry = tk.Entry(register_window, show="*") 
    password_entry.pack(pady=5)

    tk.Label(register_window, text="Country:").pack(pady=5)
    country_entry = tk.Entry(register_window)
    country_entry.pack(pady=5)

    tk.Label(register_window, text="Initial Balance:").pack(pady=5)
    balance_entry = tk.Entry(register_window)
    balance_entry.pack(pady=5)

    #function for cheking inputs and register
    def register_account():
        #assign a variable for user input
        name = name_entry.get().upper()  
        password = password_entry.get()
        country = country_entry.get().upper() 
        balance = balance_entry.get()

        # checking if inputs empty or not
        if not name or not password or not country or not balance:
            messagebox.showerror("Registration Failed", "All fields are required.") 
            return

        # checking password is digit
        if not password.isdigit() or len(password) != 6:
            messagebox.showerror("Registration Failed", "Password must be a 6-digit number.")
            return

        #checking name 
        if any(char.isdigit() for char in name):
            messagebox.showerror("Registration Failed", "you can not write any number in your name.") 
            return
        #checking country name it can not contain digit
        if any(char.isdigit() for char in country):
            messagebox.showerror("Registration Failed", "you can not write any number in your country name.")  # Error for invalid country
            return


        # checking balance
        if not balance.isdigit():
            messagebox.showerror("Registration Failed", "Balance must be a valid number.")  # Error for invalid balance
            return
        balance = int(balance)

        #generate new special account number
        accno = create_accno()

        # try insert inputs to data
        try:
            insert_data(accno, name, int(password), country, balance)
            text = "Account created successfully!\nYour account number: " + str(accno)
            messagebox.showinfo(f"Registration Successful", text)
            register_window.destroy() 
        except Exception as e:
            messagebox.showerror("Registration Failed", f"Error: {e}")

    tk.Button(register_window, text="Register", command=register_account).pack(pady=10)

    register_window.mainloop()


#create a function for create unique account number
def create_accno():
    #run till create a unique account number
    while True: 
        #create and assign new account number digits
        first_digit = random.randint(1, 9)
        remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(5))  
        random_number = int(str(first_digit) + remaining_digits)  

        cursor = dbase.execute("SELECT 1 FROM customer WHERE ACCNO = ?", (random_number,))
        #checking account number if already in database
        if not cursor.fetchone():  
            return random_number  

#create a function for fetch historical rates using by api
def fetch_historical_rates(start_date, end_date, target_currency, base_currency="GBP"):
    url = "https://api.freecurrencyapi.com/v1/historical"
    #create lists for stare rates
    rates_list = [] 
    dates_list = []  
    current_date = start_date 

    #while loop for fetching data and assign
    while current_date <= end_date:
        formatted_date = current_date.strftime("%Y-%m-%d")
        
        #define params for api key
        params = {
            "apikey": API_KEY,  
            "base_currency": base_currency, 
            "currencies": target_currency, 
            "date": formatted_date  
        }

        try:
            # make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json() 

            # check if the response contains rate data for the target date
            if "data" in data and formatted_date in data["data"]:
                rate = data["data"][formatted_date].get(target_currency)
                #if we can get rate we will add to list
                if rate:
                    rates_list.append(rate) 
                    dates_list.append(formatted_date)
                else:
                    print(f"No rate available for {formatted_date}")
            else:
                print(f"No data found for {formatted_date}: {data.get('message', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error fetching data for {formatted_date}: {e}")

        #cahnge the next day
        current_date += timedelta(days=1)

    # return the lists
    return dates_list, rates_list


# define path for database
dpath = os.path.join(os.path.dirname(__file__), "customerDatas.db")  

#conenct to database
dbase = sqlite3.connect(dpath)

# create a cursor for exacute database without any issue
cursor = dbase.cursor()

# create customer database if does not exist
dbase.execute(''' CREATE TABLE IF NOT EXISTS customer(
                accNo INT PRIMARY KEY NOT NULL, 
                name TEXT NOT NULL,              
                password INT NOT NULL,           
                location TEXT NOT NULL,         
                balance INT NOT NULL)            
''')

# map for acces databases more dynamicly
dbaseMap = {"accno": 0, "name": 1, "password": 2, "location": 3, "balance": 4} 


#function for insert customer to data base
def insert_data(ACCNO, NAME, PASSWORD, LOCATION, BALANCE):
    dbase.execute('''INSERT INTO customer(ACCNO, NAME, PASSWORD, LOCATION, BALANCE)
                    VALUES(?,?,?,?,?)''', (ACCNO, NAME, PASSWORD, LOCATION, BALANCE))
    dbase.commit()


#create function for read data from database
def read_data(id, column="ACCNO"):
    query = f"SELECT * FROM customer WHERE {column} = ?" 
    cursor = dbase.execute(query, (id,))  
    result = cursor.fetchone()  
    #return true or false base of data is exist
    return result if result else False  

#create a function for update customer from data
def update_data(column, value, id):
    query = f"UPDATE customer SET {column} = ? WHERE ACCNO = ?"
    dbase.execute(query, (value, id))
    dbase.commit() 

#delete customer from data by account number
def delete_data(id):
    dbase.execute("DELETE FROM customer WHERE ACCNO=?", (id,))
    dbase.commit() 


#create function for transfer money
def transfer(id1, id2, amount):
    #fetch data from database
    query = "SELECT ACCNO, BALANCE FROM customer WHERE ACCNO = ?"
    data = dbase.execute(query, (id1,))
    record = data.fetchone()
    balance1 = record[1] #assing customer balance 
    data = dbase.execute(query, (id2,))
    record = data.fetchone()
    balance2 = record[1] 

    # update balances after transfer
    balance1, balance2 = balance1 - amount, balance2 + amount
    update_data("BALANCE", balance1, id1)  # update balance for customer1
    update_data("BALANCE", balance2, id2)  # update balance for custoemr2
    dbase.commit()  # Save changes
    quary = f"{id1} {amount} {id2} \n"
    file_path = os.path.join(os.path.dirname(__file__), "customerFile.txt")  

    customerFile = open(file_path,"a")
    customerFile.write(quary)
    customerFile.close()

#funciton for currenct tab
def open_currency_tab():
    currency_window = tk.Toplevel()
    currency_window.title("Currency Converter")
    currency_window.geometry("300x200")

    tk.Label(currency_window, text="Enter Currency Code (e.g., USD):").pack(pady=10)
    global currency_entry
    currency_entry = tk.Entry(currency_window)
    currency_entry.pack(pady=10)
    
    #function for show currency
    def show_currency_rates():
        #assign user input
        target_currency = currency_entry.get().upper()

        # select a start and end date manually
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()

        #checking input
        if not target_currency.isalpha() or len(target_currency) != 3:
            messagebox.showerror("Invalid Currency", "Please enter a valid 3-letter currency code (e.g., USD, EUR).")
            return

        # call the funciton for fetch rates and assign
        dates, rates = fetch_historical_rates(start_date, end_date, target_currency)

        if dates and rates:
            # features for graph
            plt.figure(figsize=(10, 6))
            plt.plot(dates, rates, marker='o', color='blue', linestyle='-', linewidth=2, markersize=6)
            plt.title(f"GBP to {target_currency} (last 5 days)", fontsize=16, fontweight='bold')
            plt.xlabel("Date", fontsize=12)
            plt.ylabel(f"Exchange Rate (GBP to {target_currency})", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()

            #show the graphic
            plt.show()

        else:
            messagebox.showerror("No Data", f"No exchange rates found for {target_currency}.")

    fetch_button = tk.Button(currency_window, text="Fetch Rates", command=show_currency_rates)
    fetch_button.pack(pady=20)

    currency_window.mainloop()

#function for remove user data from database
def remove_account(data, dashboard):
    response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to remove your account? This action cannot be undone.")
    if response: 
        #try delete account
        try:
            delete_data(data[dbaseMap["accno"]]) 
            messagebox.showinfo("Account Removed", "Your account has been successfully removed.")
            dashboard.destroy()
            root.deiconify() 
            return
        #expect give the error
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove account: {e}")

#function for open transfer tab
def open_transfer_tab(data):
    
    transfer_window = tk.Toplevel()
    transfer_window.title("Transfer")
    transfer_window.geometry("300x200")

    tk.Label(transfer_window, text="Receiver Account Number:").pack(pady=5)
    receiver_entry = tk.Entry(transfer_window)
    receiver_entry.pack(pady=5)

    tk.Label(transfer_window, text="Amount:").pack(pady=5)
    amount_entry = tk.Entry(transfer_window)
    amount_entry.pack(pady=5)

    # function for execute transfer
    def execute_transfer():
        #assign user inputs
        receiver_accno = receiver_entry.get()
        amount = amount_entry.get()

        #check inputs
        if not receiver_accno or not amount:
            messagebox.showerror("Transfer Failed", "Please fill in all fields.")
            return

        if not receiver_accno.isdigit():
            messagebox.showerror("Transfer Failed", "receiver account number must be a valid number.")
            return 
        
        if not amount.isdigit():
            messagebox.showerror("Transfer Failed", "Amount must be a valid number.")
            return

        receiver_accno = int(receiver_accno)
        amount = int(amount)
        receiver_data = read_data(receiver_accno)
        #check if reciver is exist
        if not receiver_data:
            messagebox.showerror("Transfer Failed", "Receiver account does not exist.")
            return

        #execute transfer
        transfer(data[dbaseMap["accno"]], receiver_accno, amount)
        transfer_window.destroy()

    # transfer button
    tk.Button(transfer_window, text="Transfer", command=execute_transfer).pack(pady=10)
    transfer_window.mainloop()

#funciton for dashboard
def open_dashboard(data):
    # create window
    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("400x300")

    tk.Label(dashboard, text="Customer", font=("Arial", 8, "bold")).place(x=8, y=8)
    tk.Label(dashboard, text=f"Account number:\n {data[dbaseMap['accno']]}", font=("Arial", 9)).place(x=10, y=35)

    # Add buttons for features
    tk.Button(dashboard, text="Balance", command=lambda: show_balance(data)).pack(pady=5)
    tk.Button(dashboard, text="Transfer", command=lambda: open_transfer_tab(data)).pack(pady=5)
    tk.Button(dashboard, text="Currency", command=open_currency_tab).pack(pady=5)
    tk.Button(dashboard, text="Help", command=show_help).pack(pady=5)
    tk.Button(dashboard, text="Richest customers", command=display_sorted_data).pack(pady=5)

    #function for show transaction
    def show_transactions():
        # path for customerfile.txt file
        file_path = os.path.join(os.path.dirname(__file__), "customerFile.txt")  
        #try read file
        try:
            with open(file_path, "r") as file:
                transactions = file.readlines()
            emptyList = []
            #for loop for read file
            for line in transactions:
                temLine = line.split()
                #check if customer have transaction
                if int(temLine[0]) == data[dbaseMap['accno']]:
                    quary = f"You sent {temLine[1]}£ to {temLine[2]}"
                    emptyList.append(quary) 
                elif int(temLine[2]) == data[dbaseMap['accno']]:
                    quary = f"{temLine[0]} sent {temLine[1]}£ to you"
                    emptyList.append(quary) 
            
            #create new window for transactions
            transactions_window = tk.Toplevel(dashboard)
            transactions_window.title("Transaction History")
            transactions_window.geometry("400x300")

            tk.Label(transactions_window, text="Transaction History", font=("Arial", 14, "bold")).pack(pady=10)

            # showing customer transactions
            if transactions:
                for transaction in emptyList:
                    tk.Label(transactions_window, text=transaction, font=("Arial", 10)).pack(pady=2)
            else:
                tk.Label(transactions_window, text="No transactions available.", font=("Arial", 10)).pack(pady=10)

            tk.Button(transactions_window, text="Close", command=transactions_window.destroy).pack(pady=10)

        except FileNotFoundError:
            messagebox.showerror("Error", "Transaction file not found.")

    tk.Button(dashboard, text="Transactions", command=show_transactions).pack(pady=5)

    remove_button = tk.Button(dashboard, text="Remove Account", fg="red", command=lambda: remove_account(data, dashboard))
    remove_button.pack(side=tk.LEFT, padx=10, pady=20)
    dashboard.mainloop()

#function for login
def login():
    #assing user inputs
    accno = int(accno_entry.get())
    password = int(password_entry.get())
    record = read_data(accno)

    #checking inputs
    if not record:
        messagebox.showerror("Login Failed", "Account not found.")
        return
    
    if password == record[dbaseMap["password"]]:
        messagebox.showinfo("Login Successful", "Welcome, " + record[dbaseMap["name"]].lower()+"!")
        root.destroy() 
        #if everything is right opene dashboard
        open_dashboard(record)  
        return 
    else:
        messagebox.showerror("Login Failed", "Incorrect password.")

# function for show balance
def show_balance(data):
    messagebox.showinfo("Balance", f"Your balance is {data[dbaseMap['balance']]}.")
    
#function for help info
def show_help():
    messagebox.showinfo("Help", "For help, contact support@example.com.")

#main login window
root = tk.Tk()
root.title("Login Screen")
root.geometry("300x200")

# accoutn number box
tk.Label(root, text="Account Number:").pack(pady=5)
accno_entry = tk.Entry(root)
accno_entry.pack(pady=5)

# password box
tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

# login button
tk.Button(root, text="Login", command=login).pack(pady=10)

# register button
register_button = tk.Button(root, text="Register", command=open_register_tab)
register_button.place(x=220, y=160)  # Adjust position as needed

root.mainloop()  
dbase.close()  #close database