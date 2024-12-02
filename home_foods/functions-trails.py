# import smtplib
# # creates SMTP session
# s = smtplib.SMTP('smtp.gmail.com', 587)
# # start TLS for security
# s.starttls()
# # Authentication
# s.login("thetechiesvijayawada@gmail.com", "rzut fpma khbd nlic")
# # message to be sent
# message = "hello"
# # sending the mail
# s.sendmail("thetechiesvijayawada@gmail.com", "rushikasriya.pendurthi@gmail.com", message)
# # terminating the session
# s.quit()


import bcrypt

def test(password):

    # Hash the password
    bytes_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes_password, salt)
    # Return the hash as a UTF-8 string for storage
    return hash.decode('utf-8')

data = test('rushka')
print(data)

def check(password):
    stored_hashed_password = '$2b$12$ko1KOC6/39w1PHL8a6mV.OD5/orc448D1c6bBQTLgzGHBwmIFO5sy'
    user_password_bytes = password.encode('utf-8')
    print(user_password_bytes)
    # Compare the input password with the stored hash
    if bcrypt.checkpw(user_password_bytes, stored_hashed_password.encode('utf-8')):
        return True
    else:
        return False

data2 = check('rushka')
print(data2)