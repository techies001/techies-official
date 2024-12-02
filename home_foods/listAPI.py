from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import streamlit as st
from io import BytesIO
from fastapi.responses import StreamingResponse


app = FastAPI()

origins = ["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_headers=["*"],
                   allow_methods=["*"],
                   allow_credentials=True)


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


class items:
    def __init__(self, categoryId, category, numberOfItems, subCategoryId, itemName, itemDescription, weight, price):
        self.categoryId = categoryId
        self.category = category
        self.numberOfItems = numberOfItems
        self.subCategoryId = subCategoryId
        self.itemName = itemName
        self.itemDescription = itemDescription
        self.weight = weight
        self.price = price

    @staticmethod
    def list_items():
        conn = database()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """SELECT mm.id AS categoryId, mm.category, mm.numberOfItems, sm.id AS subCategoryId, sm.itemName,
                       sm.itemDescription FROM main_menu mm LEFT JOIN sub_menu sm ON mm.id = sm.categoryId
                       ORDER BY sm.id;"""
            cursor.execute(query)
            results = cursor.fetchall()
            for result in results:
                item_details = []
                sub_query = f"""select weight, price from item_details where item_id = {result['subCategoryId']}"""
                cursor.execute(sub_query)
                item_details_results = cursor.fetchall()
                item_details.append(item_details_results)
                result['itemDetails'] = item_details[0]
            return results
        except Exception as e:
            return e
        finally:
            conn.close_db()

    @staticmethod
    def get_image(image_id):
        conn = database()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """SELECT mm.category, sm.itemName, sm.itemImage FROM main_menu mm LEFT JOIN sub_menu sm ON mm.id = sm.categoryId
                           where sm.id = %s"""
            # Query to fetch the image blob by ID
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Image not found")

            image_blob = result['itemImage']  # Image binary blob

            image_name = f"{result['category']}_{result['itemName']}.jpg"

            image_stream = BytesIO(image_blob)

            headers = {
                "Content-Disposition": f"attachment; filename={image_name}"
                # This prompts the browser to download the file
            }

            return StreamingResponse(image_stream, media_type="image/jpeg", headers=headers)
        except Exception as e:
            return e
        finally:
            conn.close_db()


@app.get("/items_list_1_0")
def get_items_list():
    data = items.list_items()
    return data


@app.get("/get_image")
def display_image(image_id: int):
    result = items.get_image(image_id)
    return result


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=1111)
