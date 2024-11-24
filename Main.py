import random

def salt():
    length = 5
    start = 10 ** (length - 1)
    end = (10 ** length) - 1
    return random.randint(start, end)



def hash(pw, saltVal):
    npw = ""
    for p in pw:
        npw += str(ord(p)%10)
    res = saltVal ^ int(npw)
    if (res & 0xFFFF) < 10000:
        res *= 10
    return res


def load():
    flag = False
    while flag == False:
        userID = input("UserID: ")
        if len(userID) > 10:
            print("Choose a shorter ID")
        else:
            flag = True
    password = input("Password: ")
    saltVal = salt()
    hashed = hash(password, saltVal)

    with open('password_file.txt', 'a') as file:
        file.write(f"{userID},{saltVal},{hashed}\n")
    print(f"Password for {userID} has been stored.")
    
def verify():
    userID_input = input("Enter UserID: ")
    password_input = input("Enter Password: ")

    with open('password_file.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        stored_userID, stored_salt, stored_hash = line.split(',')
        stored_salt = int(stored_salt)
        stored_hash = int(stored_hash)

        if stored_userID == userID_input:
            input_hash = hash(password_input, stored_salt)
            if input_hash == stored_hash:
                print("ACCESS GRANTED")
                return True
            else:
                print("ACCESS DENIED")
                return False

    print("UserID not found.")
    return False
    

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
