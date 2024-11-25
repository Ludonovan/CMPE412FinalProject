import os
import ssl

import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from tkinter import Entry, Tk

load_dotenv("cred.env")
master = Tk()

def get_otp():
    return random.randint(100000,999999)

def send_otp(email, otp):
    email = email[:-1]
    my_email = str(os.getenv("EMAIL"))
    my_pass = str(os.getenv("PASS"))
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
        print("There was an error sending the OTP.")

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
        npw += str(ord(p)%10)
    res = saltVal ^ int(npw)
    if (res & 0xFFFF) < 10000:
        res *= 10
    return res

def load():
    flag = False
    userID = ""
    while not flag:
        userID = input("UserID: ")
        if len(userID) > 10:
            print("Choose a shorter ID")
        else:
            flag = True
    # password = Entry(master, bd=5, width=20, show="*")
    # password.pack()
    # master.mainloop()
    password = input("Enter Password: ")
    email = input("Email: ")
    saltVal = salt()
    hashed_pass = hash_(str(password), saltVal)

    store_password(userID, saltVal, hashed_pass, email)


def store_password(userID, salt_val, hashed_pass, hashed_email):
    with open('password_file.txt', 'a') as file:
        file.write(f"{userID},{salt_val},{hashed_pass},{hashed_email}\n")
    print(f"Password for {userID} has been stored.")


def verify():
    userID_input = input("Enter UserID: ")
    # password_input = Entry(master, bd=5, width=20, show="*")
    # password_input.pack()
    # master.mainloop()
    password_input = input("Enter Password: ")

    with open('password_file.txt', 'r') as file:
        lines = file.readlines()

    user_found = False
    for line in lines:
        stored_userID, stored_salt, stored_hash, stored_email = line.split(',')
        stored_salt = int(stored_salt)
        stored_hash = int(stored_hash)
        if stored_userID == userID_input:
            input_hash = hash_(str(password_input), stored_salt)
            if input_hash == stored_hash:
                user_found = True
                print(f"Sending OTP to {stored_email}\n")
                otp = get_otp()
                send_otp(stored_email, otp)
                user_otp = input("Enter the OTP you received: ")
                if verify_otp(int(user_otp), otp):
                    print("ACCESS GRANTED")
                else:
                    print("ACCESS DENIED")
    if not user_found:
        print("UserID not found.")

    

def main():
    inp = input("New user? (y/n): ")
    if inp == "y":
        load()
    elif inp == "n":
        verify()
    else:
        print("Something went wrong, please try again.")
        main()

if __name__ == "__main__":
    main()
