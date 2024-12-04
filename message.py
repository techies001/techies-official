from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def db_conn():
    conn = mysql.connector.connect(
        host='b1zolhaun1gzw2rk6kam-mysql.services.clever-cloud.com',
        user='uvhvti04cft8hyqp',
        password='a0dLhRmVOKPMJjI9yUDa',
        database='b1zolhaun1gzw2rk6kam'
    )
    return conn


class enquiry(BaseModel):
    name: str
    phone_no: str
    email_id: str
    message: str


@app.post("/enquiry")
async def create_analytics_report(report: enquiry):
    conn = db_conn()
    print("connected")
    cursor = conn.cursor()
    try:
        query = """
                INSERT INTO personal_form (name, phone_no, email_id, message)
                VALUES (%s, %s, %s, %s)
            """
        values = (report.name, report.phone_no, report.email_id, report.message)
        print(values)
        # Execute the query and commit the transaction
        cursor.execute(query, values)
        conn.commit()
        print("committed")
        return {"status": "success", "statusCode": 200, "message": "successful"}

    except Exception as e:
        return {"status": "failed", "statusCode": 500, "message": "record failed",
                "detail": f"Error while inserting data {e}"}
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8550)