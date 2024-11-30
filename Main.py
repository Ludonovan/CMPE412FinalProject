import os
import ssl
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel, simpledialog

load_dotenv("cred.env")

def get_otp():
    return random.randint(100000, 999999)

def send_otp(email, otp):
    email = email.strip()
    my_email = os.getenv("EMAIL")
    my_pass = os.getenv("PASS")
    if my_email is not None and my_pass is not None:
        msg = MIMEText(f"Your OTP is: {str(otp)}")
        msg['Subject'] = "Your MFA Code"
        msg['From'] = my_email
        msg['To'] = email

        context = ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)
            server.login(my_email, my_pass)
            server.sendmail(my_email, email, msg.as_string())
    else:
        messagebox.showerror("Error", "Failed to send OTP. Check your email credentials.")

def verify_otp(otp, user_otp):
    return otp == user_otp

def salt():
    length = 5
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return random.randint(start, end)

def hash_(pw, saltVal):
    npw = ""
    for p in pw:
        npw += str(ord(p) % 10)
    res = saltVal ^ int(npw)
    if (res & 0xFFFF) < 10000:
        res *= 10
    return res

def store_password(userID, salt_val, hashed_pass, email):
    with open('password_file.txt', 'a') as file:
        file.write(f"{userID},{salt_val},{hashed_pass},{email}\n")
    messagebox.showinfo("Success", f"Password for {userID} has been stored.")

def register():
    def save_user():
        userID = user_entry.get()
        password = pass_entry.get()
        email = email_entry.get()
        if len(userID) > 10:
            messagebox.showerror("Error", "UserID must be 10 characters or less.")
            return
        if not userID or not password or not email:
            messagebox.showerror("Error", "All fields are required.")
            return

        saltVal = salt()
        hashed_pass = hash_(str(password), saltVal)
        store_password(userID, saltVal, hashed_pass, email)
        register_window.destroy()

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

def login():
    userID = user_entry.get()
    password = pass_entry.get()

    if not userID or not password:
        messagebox.showerror("Error", "All fields are required.")
        return

    with open('password_file.txt', 'r') as file:
        lines = file.readlines()

    user_found = False
    for line in lines:
        stored_userID, stored_salt, stored_hash, stored_email = line.strip().split(',')
        stored_salt = int(stored_salt)
        stored_hash = int(stored_hash)
        if stored_userID == userID:
            input_hash = hash_(str(password), stored_salt)
            if input_hash == stored_hash:
                user_found = True
                otp = get_otp()
                send_otp(stored_email, otp)
                user_otp = simpledialog.askstring("OTP Verification", "Enter the OTP sent to your email:")
                if user_otp and verify_otp(int(user_otp), otp):
                    messagebox.showinfo("Success", "ACCESS GRANTED")
                else:
                    messagebox.showerror("Error", "ACCESS DENIED")
    if not user_found:
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
