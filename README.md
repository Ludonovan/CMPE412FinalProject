# A Mock UI For a Login System   
### Final project for CMPE 412 (Networks and Security) at Shippensburg University.  


#### Features:
- Basic GUI using tkinter
- Account Registration and login
- Multifactor authentication through email using GMail SMTP server.
- Passwords hashing using SHA256 and a generated salt value.  
- Encryption of username and email using Fernet.  
- Database to store user data using SQLite.  
- Loading of sensitive data in '.env' files using dotenv
  - Ensures credentials are not hardcoded

#### Future Improvements:
- Implement a reset password feature
- Implement better database so things aren't stored locally
- Implement better key storage
- Improve error messages


