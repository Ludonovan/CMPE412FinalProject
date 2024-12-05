import os
import random
import ssl
import smtplib
from email.mime.text import MIMEText
import sqlite3
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel, simpledialog
import re

# Load email credentials for gmail SMTP server
load_dotenv('cred.env')

# Initialize database
db = sqlite3.connect('users.db')
cursor = db.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT UNIQUE NOT NULL,
    salt INTEGER NOT NULL,
    hashed_password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
''')
db.commit()

# Load a key value used for encryption
def load_key(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            return file.read()

# Create separate keys for username and email encryption
uname_key = load_key('uname.key')
email_key = load_key('email.key')
uname_f = Fernet(uname_key)
email_f = Fernet(email_key)

# Create a random 6-digit one-time passcode
def get_otp():
    return random.randint(100000, 999999)

# Send a user a code for MFA
def send_otp(email, otp):
    email = email.strip()
    my_email = os.getenv('EMAIL')
    my_pass = os.getenv('PASS')
    if my_email and my_pass:
        msg = MIMEText(f"Your one-time password is: {str(otp)}")
        msg['Subject'] = "Your MFA Code"
        msg['From'] = my_email
        msg['To'] = email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(my_email, my_pass)
            server.sendmail(my_email, email, msg.as_string())
    else:
        messagebox.showerror("Error", "Failed to send OTP. Check your email credentials.")

# Verify that the user-entered OTP is the same as the one that was sent
def verify_otp(otp, user_otp):
    return otp == user_otp

# Generate a salt within the 64-bit signed integer range
def salt():
    return random.randint(0, 2**63 - 1)

# Use SHA256 to hash a password using a salt value
def hash_password(password, salt_value):
    hasher = hashlib.sha256()
    pwd_with_salt = f"{password}{salt_value}".encode()
    hasher.update(pwd_with_salt)
    return hasher.hexdigest()

# Validate password strength
def is_strong_password(password):
    if len(password) < 10:
        return "Password must be at least 10 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must include at least one uppercase letter."
    if not re.search(r'\d', password):
        return "Password must include at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must include at least one special character."
    return "Strong"

# Make sure the entered email is valid
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Store encrypted username, salt value, hashed password, and encrypted email
def store_password(user, salt_val, hashed_pass, email):
    try:
        cursor.execute('''
        INSERT INTO users (user_id, salt, hashed_password, email)
        VALUES (?, ?, ?, ?)
        ''', (user, salt_val, hashed_pass, email))
        db.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {e}")
        messagebox.showerror("Error", "UserID or Email already exists.")

# Register an account
def register():
    def save_user():
        userID = user_entry.get()
        # Validate username length
        if len(userID) > 20:
            messagebox.showerror("Error", "UserID must be 20 characters or less.")
            return

        password = pass_entry.get()
        # Validate password strength
        password_strength = is_strong_password(password)
        if password_strength != "Strong":
            messagebox.showerror("Error", password_strength)
            return

        email = email_entry.get()
        # Make sure email is valid
        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email address.")
            return

        if not userID or not password or not email:
            messagebox.showerror("Error", "All fields are required.")
            return





        # Encrypt username and email
        encrypted_uname = uname_f.encrypt(userID.encode()).decode()
        encrypted_email = email_f.encrypt(email.encode()).decode()

        # Hash password with generated salt value
        salt_val = salt()
        hashed_pass = hash_password(password, salt_val)

        # Store user data
        try:
            cursor.execute('''
            INSERT INTO users (user_id, salt, hashed_password, email)
            VALUES (?, ?, ?, ?)
            ''', (encrypted_uname, salt_val, hashed_pass, encrypted_email))
            db.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "UserID or Email already exists.")
        register_window.destroy()

    # Register UI
    register_window = Toplevel()
    register_window.title("Register")
    register_window.geometry("300x200")

    Label(register_window, text="UserID:").pack()
    user_entry = Entry(register_window)
    user_entry.pack()

    Label(register_window, text="Password:").pack()
    pass_entry = Entry(register_window, show="*")
    pass_entry.pack()

    Label(register_window, text="Email:").pack()
    email_entry = Entry(register_window)
    email_entry.pack()

    Button(register_window, text="Register", command=save_user).pack()

# Validate a username and password
# Send user a one time passcode and verify
def login():
    # Get user inputs
    userID = user_entry.get()
    password = pass_entry.get()

    if not userID or not password:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Look for matching user id
    cursor.execute('SELECT user_id, salt, hashed_password, email FROM users')
    result = None
    for r in cursor.fetchall():
        try:
            dec = uname_f.decrypt(r[0].encode()).decode()
            if dec == userID:
                result = r
                break
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
            return

    # If id found, send otp and verify
    if result:
        stored_username, stored_salt, stored_hash, stored_email = result

        # Ensure stored_email is in bytes before decrypting
        if isinstance(stored_email, str):
            stored_email = stored_email.encode()

        input_hash = hash_password(password, stored_salt)
        if input_hash == stored_hash:
            try:
                decrypted_email = email_f.decrypt(stored_email).decode()
                otp = get_otp()
                send_otp(decrypted_email, otp)
                user_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to " + decrypted_email + ": ")
                if user_otp and verify_otp(otp, int(user_otp)):
                    messagebox.showinfo("Success", "ACCESS GRANTED")
                else:
                    messagebox.showerror("Error", "ACCESS DENIED")
            except Exception as e:
                messagebox.showerror("Error", f"Email decryption failed: {str(e)}")
        else:
            messagebox.showerror("Error", "Incorrect password.")
    else:
        messagebox.showerror("Error", "UserID not found.")

# Main UI
root = Tk()
root.title("Login")
root.geometry("300x200")

Label(root, text="UserID:").pack()
user_entry = Entry(root)
user_entry.pack()

Label(root, text="Password:").pack()
pass_entry = Entry(root, show="*")
pass_entry.pack()

Button(root, text="Login", command=login).pack(pady=5)
Button(root, text="Register", command=register).pack(pady=5)

root.mainloop()
