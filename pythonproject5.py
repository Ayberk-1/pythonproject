import sqlite3
import random 
import tkinter as tk
import sqlite3
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

#FreeCurrencyAPI key
API_KEY = "fca_live_bStX1hF5ZdIq2wEM0CQzUudy4CwdqK0bUdleidtE"

def bubble_sort(customers):
    n = len(customers)
    for i in range(n):
        for j in range(0, n-i-1):
            # Compare balances (index 4 is the balance)
            if customers[j][dbaseMap["balance"]] < customers[j+1][dbaseMap["balance"]]:
                # Swap if the current balance is greater than the next
                customers[j], customers[j+1] = customers[j+1], customers[j]
    return customers

def display_sorted_data():
    # Create a new window to display sorted customer data
    sorted_data_window = tk.Toplevel()
    sorted_data_window.title("Richest customers")  # Title of the window
    sorted_data_window.geometry("400x400")  # Set the window size

    # Fetch all customer data from the database
    cursor = dbase.execute("SELECT * FROM customer")
    customers = cursor.fetchall()

    # Sort the customers by balance in descending order
    sorted_customers = bubble_sort(customers)

    # Add a title label to the window
    tk.Label(sorted_data_window, text="Sorted Customers by Balance", font=("Arial", 14, "bold")).pack(pady=10)

    # Create a frame to hold the sorted data
    data_frame = tk.Frame(sorted_data_window)
    data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add column headers for Name, Location, and Balance
    headers = ["Name", "Location", "Balance"]
    for i, header in enumerate(headers):
        tk.Label(data_frame, text=header, font=("Arial", 10, "bold"), relief=tk.GROOVE, width=15).grid(row=0, column=i)

    # Populate the rows with the sorted data
    for row_index, customer in enumerate(sorted_customers, start=1):
        # Extract Name, Location, and Balance fields
        values = [customer[1], customer[3], customer[4]]
        for col_index, value in enumerate(values):
            tk.Label(data_frame, text=value, font=("Arial", 10), relief=tk.RIDGE, width=15).grid(row=row_index, column=col_index)

    # Add a close button to close the window
    tk.Button(sorted_data_window, text="Close", command=sorted_data_window.destroy).pack(pady=10)

def open_register_tab():
    # Create a new window for the registration process
    register_window = tk.Toplevel()
    register_window.title("Register New Account")  # Title of the registration window
    register_window.geometry("300x300")  # Set the size of the window

    # Input field for Name
    tk.Label(register_window, text="Name:").pack(pady=5)
    name_entry = tk.Entry(register_window)
    name_entry.pack(pady=5)

    # Input field for Password
    tk.Label(register_window, text="Password (6 digits):").pack(pady=5)
    password_entry = tk.Entry(register_window, show="*")  # Password hidden with '*'
    password_entry.pack(pady=5)

    # Input field for Country
    tk.Label(register_window, text="Country:").pack(pady=5)
    country_entry = tk.Entry(register_window)
    country_entry.pack(pady=5)

    # Input field for Initial Balance
    tk.Label(register_window, text="Initial Balance:").pack(pady=5)
    balance_entry = tk.Entry(register_window)
    balance_entry.pack(pady=5)

    def register_account():
        # Retrieve the values entered by the user
        name = name_entry.get().upper()  # Convert name to uppercase for consistency
        password = password_entry.get()
        country = country_entry.get().upper()  # Convert country to uppercase for consistency
        balance = balance_entry.get()

        # Validate that all fields are filled
        if not name or not password or not country or not balance:
            messagebox.showerror("Registration Failed", "All fields are required.")  # Show error for empty fields
            return

        # Validate password - must be a 6-digit number
        if not password.isdigit() or len(password) != 6:
            messagebox.showerror("Registration Failed", "Password must be a 6-digit number.")  # Error for invalid password
            return

        # Validate balance - must be a valid number
        if not balance.isdigit():
            messagebox.showerror("Registration Failed", "Balance must be a valid number.")  # Error for invalid balance
            return

        # Convert balance to integer for database storage
        balance = int(balance)

        # Generate a new account number
        accno = create_accno()

        # Try to insert the new account into the database
        try:
            insert_data(accno, name, int(password), country, balance)
            # Show success message with the new account number
            text = "Account created successfully!\nYour account number: " + str(accno)
            messagebox.showinfo(f"Registration Successful", text)
            register_window.destroy()  # Close the registration window
        except Exception as e:
            # Show an error message if account creation fails
            messagebox.showerror("Registration Failed", f"Error: {e}")

    # Button to submit the registration form
    tk.Button(register_window, text="Register", command=register_account).pack(pady=10)

    # Start the Tkinter event loop for the registration window
    register_window.mainloop()


def create_accno():
    while True:  # Keep trying until a unique account number is generated
        # Generate a random 6-digit account number
        first_digit = random.randint(1, 9)  # Ensure the first digit is not 0
        remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(5))  # Generate the remaining 5 digits
        random_number = int(str(first_digit) + remaining_digits)  # Combine to form a 6-digit number

        # Check if the generated number already exists in the customer database
        cursor = dbase.execute("SELECT 1 FROM customer WHERE ACCNO = ?", (random_number,))
        if not cursor.fetchone():  # If no match is found, the number is unique
            return random_number  # Return the unique account number


def fetch_historical_rates(start_date, end_date, target_currency, base_currency="GBP"):
    # Define the FreeCurrencyAPI endpoint for historical exchange rates
    url = "https://api.freecurrencyapi.com/v1/historical"
    rates_list = []  # List to store the exchange rates
    dates_list = []  # List to store the corresponding dates
    current_date = start_date  # Start date for fetching rates

    # Loop through each day between start_date and end_date
    while current_date <= end_date:
        # Format the date as YYYY-MM-DD for the API request
        formatted_date = current_date.strftime("%Y-%m-%d")
        
        # Define the parameters for the API request
        params = {
            "apikey": API_KEY,  # API key for authentication
            "base_currency": base_currency,  # Base currency (default: GBP)
            "currencies": target_currency,  # Target currency to fetch rates for
            "date": formatted_date  # The specific date for historical data
        }

        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()  # Parse the JSON response

            # Check if the response contains rate data for the target date
            if "data" in data and formatted_date in data["data"]:
                # Extract the exchange rate for the target currency
                rate = data["data"][formatted_date].get(target_currency)
                if rate:
                    rates_list.append(rate)  # Add the rate to the list
                    dates_list.append(formatted_date)  # Add the corresponding date
                else:
                    # Handle case where the rate is missing for the date
                    print(f"No rate available for {formatted_date}")
            else:
                # Handle case where no data is returned for the date
                print(f"No data found for {formatted_date}: {data.get('message', 'Unknown error')}")
        
        except Exception as e:
            # Handle exceptions during the API request
            print(f"Error fetching data for {formatted_date}: {e}")

        # Move to the next day
        current_date += timedelta(days=1)

    # Return the list of dates and their corresponding exchange rates
    return dates_list, rates_list


# Define the path to the SQLite database file
dpath = os.path.join(os.path.dirname(__file__), "bank_data5.db")  # Combine the directory of the script with the database filename

# Connect to the SQLite database (creates the file if it doesn't exist)
dbase = sqlite3.connect(dpath)

# Create a cursor object to execute SQL commands
cursor = dbase.cursor()

# Create the 'customer' table if it doesn't already exist
dbase.execute(''' CREATE TABLE IF NOT EXISTS customer(
                accNo INT PRIMARY KEY NOT NULL, 
                name TEXT NOT NULL,              
                password INT NOT NULL,           
                location TEXT NOT NULL,         
                balance INT NOT NULL)            
''')

# Map for easy access to column indices in database queries
dbaseMap = {"accno": 0, "name": 1, "password": 2, "location": 3, "balance": 4}  # Column names mapped to their positions


def insert_data(ACCNO, NAME, PASSWORD, LOCATION, BALANCE):
    # Insert a new customer record into the 'customer' table
    # Use placeholders (?) to safely insert data and prevent SQL injection
    dbase.execute('''INSERT INTO customer(ACCNO, NAME, PASSWORD, LOCATION, BALANCE)
                    VALUES(?,?,?,?,?)''', (ACCNO, NAME, PASSWORD, LOCATION, BALANCE))
    dbase.commit()  # Commit the transaction to save changes to the database

def read_data(id, column="ACCNO"):
    # Retrieve a customer record from the 'customer' table based on a specified column and value
    # By default, it searches by 'ACCNO' unless another column is specified
    query = f"SELECT * FROM customer WHERE {column} = ?"  # Prepare SQL query dynamically
    cursor = dbase.execute(query, (id,))  # Execute query with provided ID
    result = cursor.fetchone()  # Fetch one matching record
    return result if result else False  # Return the record if found; otherwise, return False




def update_data(column, value, id):
    # Update a column for a specific account
    query = f"UPDATE customer SET {column} = ? WHERE ACCNO = ?"
    dbase.execute(query, (value, id))
    dbase.commit()  # Save changes

def delete_data(id):
    # Delete a customer by account number
    dbase.execute("DELETE FROM customer WHERE ACCNO=?", (id,))
    dbase.commit()  # Save changes


def transfer(id1, id2, amount):
    # Fetch balance of both accounts
    query = "SELECT ACCNO, BALANCE FROM customer WHERE ACCNO = ?"
    data = dbase.execute(query, (id1,))
    record = data.fetchone()
    balance1 = record[1]  # Balance of first account
    data = dbase.execute(query, (id2,))
    record = data.fetchone()
    balance2 = record[1]  # Balance of second account

    # Update balances after transfer
    balance1, balance2 = balance1 - amount, balance2 + amount
    update_data("BALANCE", balance1, id1)  # Update balance for id1
    update_data("BALANCE", balance2, id2)  # Update balance for id2
    dbase.commit()  # Save changes
    quary = f"{id1} {amount} {id2} \n"
    file_path = os.path.join(os.getcwd(), "customerFile.txt")

    customerFile = open(file_path,"a")
    customerFile.write(quary)
    customerFile.close()

def show_currency_rates():
    # Get user input currency and convert to uppercase
    target_currency = currency_entry.get().upper()

    # Manually set the start and end dates
    start_date = datetime(2023, 1, 1)  # Start Date (example)
    end_date = datetime(2023, 1, 4)   # End Date (example)

    if not target_currency.isalpha() or len(target_currency) != 3:
        messagebox.showerror("Invalid Currency", "Please enter a valid 3-letter currency code (e.g., USD, EUR).")
        return

    # Fetch historical exchange rates
    rates = fetch_historical_rates(start_date, end_date, target_currency)

    if rates:
        messagebox.showinfo("Currency Data", f"Exchange Rates for {target_currency}: {rates}")
    else:
        messagebox.showerror("No Data", f"No exchange rates found for {target_currency}.")

def open_currency_tab():
    # Create a new window for the currency feature
    currency_window = tk.Toplevel()
    currency_window.title("Currency Converter")
    currency_window.geometry("300x200")

    # Add label and input field for currency code
    tk.Label(currency_window, text="Enter Currency Code (e.g., USD):").pack(pady=10)
    global currency_entry
    currency_entry = tk.Entry(currency_window)
    currency_entry.pack(pady=10)
    
    # Define function to show currency rates
    def show_currency_rates():
        target_currency = currency_entry.get().upper()

        # Manually set the start and end dates for historical data (example: last 5 days)
        start_date = datetime.now() - timedelta(days=5)
        end_date = datetime.now()

        if not target_currency.isalpha() or len(target_currency) != 3:
            messagebox.showerror("Invalid Currency", "Please enter a valid 3-letter currency code (e.g., USD, EUR).")
            return

        # Fetch historical exchange rates
        dates, rates = fetch_historical_rates(start_date, end_date, target_currency)

        if dates and rates:
            # Create a plot of the data
            plt.figure(figsize=(10, 6))
            plt.plot(dates, rates, marker='o', color='blue', linestyle='-', linewidth=2, markersize=6)
            plt.title(f"GBP to {target_currency} (last 5 days)", fontsize=16, fontweight='bold')
            plt.xlabel("Date", fontsize=12)
            plt.ylabel(f"Exchange Rate (GBP to {target_currency})", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()

            # Show the plot in a new window
            plt.show()

        else:
            messagebox.showerror("No Data", f"No exchange rates found for {target_currency}.")

    # Add button to fetch rates
    fetch_button = tk.Button(currency_window, text="Fetch Rates", command=show_currency_rates)
    fetch_button.pack(pady=20)

    # Start the currency window loop
    currency_window.mainloop()

def remove_account(data, dashboard):
    # Confirm account deletion
    response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to remove your account? This action cannot be undone.")
    if response:  # If the user confirms
        try:
            delete_data(data[dbaseMap["accno"]])  # Delete the account
            messagebox.showinfo("Account Removed", "Your account has been successfully removed.")
            # Close the dashboard and return to the login screen
            dashboard.destroy()
            root.deiconify()  # Show the login window again
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove account: {e}")

def open_transfer_tab(data):
    # New window for transfer
    
    transfer_window = tk.Toplevel()
    transfer_window.title("Transfer")
    transfer_window.geometry("300x200")

    # Add input fields for receiver account and amount
    tk.Label(transfer_window, text="Receiver Account Number:").pack(pady=5)
    receiver_entry = tk.Entry(transfer_window)
    receiver_entry.pack(pady=5)

    tk.Label(transfer_window, text="Amount:").pack(pady=5)
    amount_entry = tk.Entry(transfer_window)
    amount_entry.pack(pady=5)

    # Define function to execute transfer
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

def show_transactions():
        # Show the transaction history
        file_path = os.path.join(os.getcwd(), "customerFile.txt")
        try:
            with open(file_path, "r") as file:
                transactions = file.readlines()

            # Create a new window to display transactions
            transactions_window = tk.Toplevel(dashboard)
            transactions_window.title("Transaction History")
            transactions_window.geometry("400x300")

            # Add a label for transactions
            tk.Label(transactions_window, text="Transaction History", font=("Arial", 14, "bold")).pack(pady=10)

            # Display each transaction in the new window
            if transactions:
                for transaction in transactions:
                    tk.Label(transactions_window, text=transaction, font=("Arial", 10)).pack(pady=2)
            else:
                tk.Label(transactions_window, text="No transactions available.", font=("Arial", 10)).pack(pady=10)

            # Add a close button to the transaction window
            tk.Button(transactions_window, text="Close", command=transactions_window.destroy).pack(pady=10)

        except FileNotFoundError:
            messagebox.showerror("Error", "Transaction file not found.")

def open_dashboard(data):
    # New window for customer dashboard
    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry("400x300")

    # Display customer details
    tk.Label(dashboard, text="Customer", font=("Arial", 8, "bold")).place(x=8, y=8)
    tk.Label(dashboard, text=f"Account number:\n {data[dbaseMap['accno']]}", font=("Arial", 9)).place(x=10, y=35)

    # Add buttons for various actions
    tk.Button(dashboard, text="Balance", command=lambda: show_balance(data)).pack(pady=5)
    tk.Button(dashboard, text="Transfer", command=lambda: open_transfer_tab(data)).pack(pady=5)
    tk.Button(dashboard, text="Currency", command=open_currency_tab).pack(pady=5)
    tk.Button(dashboard, text="Help", command=show_help).pack(pady=5)
    tk.Button(dashboard, text="Richest customers", command=display_sorted_data).pack(pady=5)
    def show_transactions():
        # Show the transaction history
        file_path = os.path.join(os.getcwd(), "customerFile.txt")
        try:
            with open(file_path, "r") as file:
                transactions = file.readlines()
            emptyList = []
            for line in transactions:
                temLine = line.split()
                if int(temLine[0]) == data[dbaseMap['accno']]:
                    quary = f"{temLine[0]}(you) sent {temLine[1]} to {temLine[2]}"
                    emptyList.append(quary) 
                elif int(temLine[2]) == data[dbaseMap['accno']]:
                    quary = f"{temLine[0]} sent {temLine[1]} to {temLine[2]}(you)"
                    emptyList.append(quary) 
            # Create a new window to display transactions
            transactions_window = tk.Toplevel(dashboard)
            transactions_window.title("Transaction History")
            transactions_window.geometry("400x300")

            # Add a label for transactions
            tk.Label(transactions_window, text="Transaction History", font=("Arial", 14, "bold")).pack(pady=10)

            # Display each transaction in the new window
            if transactions:
                for transaction in emptyList:
                    tk.Label(transactions_window, text=transaction, font=("Arial", 10)).pack(pady=2)
            else:
                tk.Label(transactions_window, text="No transactions available.", font=("Arial", 10)).pack(pady=10)

            # Add a close button to the transaction window
            tk.Button(transactions_window, text="Close", command=transactions_window.destroy).pack(pady=10)

        except FileNotFoundError:
            messagebox.showerror("Error", "Transaction file not found.")

    tk.Button(dashboard, text="Transactions", command=show_transactions).pack(pady=5)

    # Remove account button
    remove_button = tk.Button(dashboard, text="Remove Account", fg="red", command=lambda: remove_account(data, dashboard))
    remove_button.pack(side=tk.LEFT, padx=10, pady=20)
    dashboard.mainloop()

def login():
    # Attempt to login with account number and password
    accno = int(accno_entry.get())
    password = int(password_entry.get())
    record = read_data(accno)

    if not record:
        messagebox.showerror("Login Failed", "Account not found.")
        return
    
    if password == record[dbaseMap["password"]]:
        messagebox.showinfo("Login Successful", "Welcome, " + record[dbaseMap["name"]].lower())
        root.destroy()  # Close the login window
        open_dashboard(record)  # Open the dashboard
        return 
    else:
        messagebox.showerror("Login Failed", "Incorrect password.")

# Function to show balance
def show_balance(data):
    messagebox.showinfo("Balance", f"Your balance is {data[dbaseMap['balance']]}.")
    
# Function to show help
def show_help():
    messagebox.showinfo("Help", "For help, contact support@example.com.")

# Main login window
root = tk.Tk()
root.title("Login Screen")
root.geometry("300x200")

# Account number input field
tk.Label(root, text="Account Number:").pack(pady=5)
accno_entry = tk.Entry(root)
accno_entry.pack(pady=5)

# Password input field
tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

# Login button
tk.Button(root, text="Login", command=login).pack(pady=10)

# Register button for new users
register_button = tk.Button(root, text="Register", command=open_register_tab)
register_button.place(x=220, y=160)  # Adjust position as needed

root.mainloop()  # Start the main loop for the login window
dbase.close()  # Close the database connection when the program ends


