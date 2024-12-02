from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import random
import string
import bcrypt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pydantic import BaseModel

app = FastAPI()

origin = ["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origin,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


class database:
    def __init__(self):
        self.conn = mysql.connector.connect(user='root',
                                            host='localhost',
                                            password='',
                                            database='home_foods'
                                            )

    def cursor(self, dictionary=False):
        return self.conn.cursor(dictionary=dictionary)

    def commit(self):
        return self.conn.commit()

    def close_db(self):
        return self.conn.close()


class users:
    def __init__(self, email: str, password: str, firstname: str, lastname: str):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def userToken():
        first_part = ''.join(random.choices(string.ascii_letters, k=6))
        second_part = random.randint(3, 99)
        third_part = ''.join(random.choices(string.ascii_letters, k=6))
        fouth_part = ''.join(random.choices(string.ascii_letters, k=6))
        token = f"{first_part}-{str(second_part)}{third_part}-{fouth_part}"
        return token

    @staticmethod
    def encrypt_password(password):
        bytes_password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes_password, salt)
        return hash.decode('utf-8')

    @staticmethod
    def passcode_generator():
        passcode = random.randint(10000, 99999)
        return passcode

    def sign_up(self):
        conn = database()
        cursor = conn.cursor()
        response = {}
        try:
            # userToken = users()
            token_response = users.userToken()
            # pass_access = users(self.email, self.password, self.firstname, self.lastname)
            password = self.encrypt_password(self.password)
            query = "insert into users(userToken, email, password, firstName, lastName)values(%s, %s, %s, %s, %s)"
            values = (token_response, self.email, password, self.firstname, self.lastname)
            cursor.execute(query, values)
            conn.commit()
            response = {"status": "Success", "statusCode": 200, "message": "Sign-up successful"}

        except Exception as e:
            response = {"status": "Failed", "statusCode": 500, "message": f"Sign-up Failed : {e}"}
        finally:
            conn.close_db()

            return response

    @staticmethod
    def login(email: str = Query(..., description="provide email"),
              password: str = Query(..., description="provide password")):
        conn = database()
        cursor = conn.cursor(dictionary=True)
        response = {}
        try:
            query = f"select * from users where email = '{email}'"
            cursor.execute(query)
            results = cursor.fetchone()
            print(results)
            actual_password = results['password']
            userBytes = password.encode('utf-8')
            status = bcrypt.checkpw(userBytes, actual_password.encode('utf-8'))
            print("status----------------------->>>", status)

            if status == True:
                response = {
                    "status": "Success", "statusCode": 200, "message": "Login successful", "data": {
                        "userToken": results["userToken"],
                        "email": results["email"],
                        "password": results["password"],
                        "firstName": results["firstName"],
                        "lastName": results["lastName"]
                    }
                }
            else:
                response = {"status": "Failed", "statusCode": 401, "message": "Login Failed. Invalid Login Details"}
        except Exception as e:
            response = {"status": "Failed", "statusCode": 500, "message": f"Login Failed : {e}"}
        finally:
            conn.close_db()
            return response

    @staticmethod
    def send_reset_passcode(email, passcode):
        import smtplib
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("thetechiesvijayawada@gmail.com", "rzut fpma khbd nlic")
        message = MIMEMultipart()
        message['From'] = "thetechiesvijayawada@gmail.com"
        message['To'] = email
        message['Subject'] = "OTP - RESET PASSWORD"
        description = f"OTP To Reset Password is {passcode}"
        message.attach(MIMEText(description, 'html'))
        s.sendmail("thetechiesvijayawada@gmail.com", f"{email}", message.as_string())
        s.quit()
        return {"status": "Passcode Sent"}

    @staticmethod
    def send_store_passcode(email):
        conn = database()
        cursor = conn.cursor(dictionary=True)
        try:
            query = f"select * from users where email = '{email}'"
            cursor.execute(query)
            email_results = cursor.fetchall()
            if len(email_results) > 0:
                email_exists = True
                passcode = users.passcode_generator()
                generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(passcode)
                passcode_record = f"update users set resetPasscode = '{passcode}', timeOfReset = '{generated_time}' where email = '{email}'"
                cursor.execute(passcode_record)
                conn.commit()
                send_email = users.send_reset_passcode(email, passcode)
                print(send_email)
                # passcode_expiry_time = (datetime.strptime(generated_time, "%Y-%m-%d %H:%M:%S") + timedelta(seconds=25)).strftime(
                #     "%Y-%m-%d %H:%M:%S")
                # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # actual_current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                # if actual_current_time == passcode_expiry_time:
                #     passcode_expiry_query = f"update users set resetPasscode = '' "
                #     cursor.execute(passcode_expiry_query)
                #     conn.commit()
                # # else:
                # #
                return {"status": "Success", "statusCode": 200, "message": f"Reset Passcode Sent to Email : {email}"}
            else:
                email_exists = False
                return {"status": "Failed", "statusCode": 401, "message": "User Not Found"}
        except Exception as e:
            return {"status": "Failed", "statusCode": 500, "message": f"Failed to Reset Password"}
        finally:
            conn.close_db()

    @staticmethod
    def update_forgot_password(email, passcode, newPassword):
        conn = database()
        cursor = conn.cursor(dictionary=True)
        try:
            check_passcode = f"select resetPasscode from users where email = '{email}'"
            cursor.execute(check_passcode)
            db_passcode = cursor.fetchone()
            if db_passcode['resetPasscode'] == passcode:
                new_password_hash_object = users.encrypt_password(newPassword)
                update_password = f'update users set password = "{new_password_hash_object}" where email = "{email}"'
                cursor.execute(update_password, )
                conn.commit()
                return {"status": "Success", "statusCode": 200, "message": "Password changed successfully"}
            else:
                return {"status": "Failed", "statusCode": 401, "message": "Please Provide Valid OTP"}
        except Exception as e:
            return {"status": "Failed", "statusCode": 500, "message": f"{e}"}
        finally:
            conn.close_db()

    @staticmethod
    def reset_password(email, old_password, new_password):
        conn = database()
        cursor = conn.cursor(dictionary=True)
        try:
            get_existing_details = f'select * from users where email = "{email}"'
            cursor.execute(get_existing_details)
            results = cursor.fetchone()
            actual_password = results['password']
            userBytes = old_password.encode('utf-8')
            status = bcrypt.checkpw(userBytes, actual_password.encode('utf-8'))
            print("status----------------------->>>", status)
            if status == True:
                new_password = users.encrypt_password(new_password)
                update_new_password = f'update users set password = %s where email = %s'
                values = (new_password, email)
                cursor.execute(update_new_password, values)
                conn.commit()
                return {"status": "success", "statusCode": 200, "message": "Password Reset Successful"}
            else:
                return {"status": "Failed", "statusCode": 401, "message": "Incorrect Password"}
        except Exception as e:
            return {"status": "Failed", "statusCode": 500, "message": f"Password Reset Failed {e}"}
        finally:
            conn.close_db()

class sign_up_data(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str


@app.post("/sign-up")
async def sign_up_user(request: sign_up_data):
    data = users(request.email, request.password, request.firstName, request.lastName)
    sign_up_response = data.sign_up()
    return sign_up_response

class login_data(BaseModel):
    email: str
    password: str

@app.get("/login")
def login_response(request: login_data):
    data = users.login(request.email, request.password)
    return data

class passcode_data(BaseModel):
    email: str


@app.get("/send-rest-passcode")
async def send_reset_passcode(request: passcode_data):
    data = users.send_store_passcode(request.email)
    return data


class update_password_data(BaseModel):
    email: str
    otp: str
    newPassword: str


@app.post("/update-password")
async def update_password(request: update_password_data):
    data = users.update_forgot_password(request.email, request.otp, request.newPassword)
    return data


class reset_password_data(BaseModel):
    email: str
    currentPassword: str
    newPassword: str


@app.post("/reset-password")
async def reset_password(request: reset_password_data):
    data = users.reset_password(request.email, request.currentPassword, request.newPassword)
    return data


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=2222)
