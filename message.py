from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow all origins for CORS (cross-origin requests)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection parameters
db_config = {
    'host': '192.168.0.127',
    'user': 'root',
    'password': 'root',
    'database': 'home_foods',
}



class enquiry(BaseModel):
    name: str
    phone_no: str
    email_id: str
    message: str




##### form data

@app.post("/enquiry")
async def create_analytics_report(report: enquiry):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:


        # SQL query to insert data
        query = """
                INSERT INTO personal_form (name, phone_no, email_id, message)
                VALUES (%s, %s, %s, %s)
            """
        values = (report.name, report.phone_no, report.email_id, report.message)

        # Execute the query and commit the transaction
        cursor.execute(query, values)
        conn.commit()
        return {"status": "success", "statusCode": 200, "message": "successful"}

    except Exception as e:
        return {"status": "failed", "statusCode": 500, "message": "record failed",
                "detail": f"Error while inserting data {e}"}
    finally:
        cursor.close()
        conn.close


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8550)