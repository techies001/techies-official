from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import mysql.connector
from io import BytesIO


app = FastAPI()

db = mysql.connector.connect(
    user='root',
    host='localhost',
    password='',
    database='home_foods'
)


@app.get("/download_image/{image_id}")
async def download_image(image_id: int):
    try:
        cursor = db.cursor(dictionary=True)
        query = """SELECT mm.category, sm.itemName, sm.itemImage FROM main_menu mm LEFT JOIN sub_menu sm ON mm.id = sm.categoryId
                       where sm.id = %s"""
        # Query to fetch the image blob by ID
        cursor.execute(query, (image_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Image not found")

        image_blob = result['itemImage']  # Image binary blob

        # If the image name is not stored, you can use a default name or derive it somehow
        image_name = f"{result['category']}_{result['itemName']}.jpg"  # Default name for the image

        # Convert the image blob into a BytesIO object
        image_stream = BytesIO(image_blob)

        # Set the response headers for downloading
        headers = {
            "Content-Disposition": f"attachment; filename={image_name}"  # This prompts the browser to download the file
        }

        # Return the image as a downloadable file
        return StreamingResponse(image_stream, media_type="image/jpeg", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
