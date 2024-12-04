# SALTED: A Mock UI For a Login System   
### Final project for CMPE 412 (Networks and Security) at Shippensburg University.  


#### Features:
- "Account" Registration and Login with multifactor authentication through email using GMail SMTP server.
- Passwords hashed using SHA256 and a generated salt value.  
- Encryption of username and email using Fernet.  
- Database to store user data using SQLite.  

#### Future Improvements
- Check for valididity of emails during registration
- Check that passwords are strong passwords (10+ chars, uppercase, nums, special char)
  - Update UI with password strength
- Make sure 2 people cant use the same email
- Reset password feature
