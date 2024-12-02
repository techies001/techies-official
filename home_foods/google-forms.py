from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origin = ["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origin,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
# Your OAuth credentials
CLIENT_ID = "1061361896514-k20p2tb5lg1rsekh2k51265ci7b8b3gq.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8000/callback"
# SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
SCOPES = "https://www.googleapis.com/auth/forms.body"
FORM_RESPONSE_SCOPES = "https://www.googleapis.com/auth/forms.responses"

# Google's OAuth 2.0 endpoints
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"


@app.get("/")
async def login():
    """
    Step 1: Redirect user to Google's OAuth 2.0 authorization page.
    """
    auth_url = (
        f"{AUTH_URI}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES, FORM_RESPONSE_SCOPES}"
        f"&access_type=offline"
    )
    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
    """
    Step 2: Handle the OAuth 2.0 callback from Google.
    Exchange the authorization code for an access token.
    """
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(content={"error": "Authorization failed. No code provided."}, status_code=400)

    # Exchange authorization code for access token
    token_response = requests.post(
        TOKEN_URI,
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )

    if token_response.status_code == 200:
        tokens = token_response.json()
        return JSONResponse(
            content={
                "message": "Access token obtained successfully!",
                "tokens": tokens,
            }
        )
    else:
        return JSONResponse(
            content={"error": token_response.json()}, status_code=token_response.status_code
        )


@app.post("/create-form")
def create_form(token: str):
    """
    Step 3: Use the access token to call the Google Forms API.
    """
    form_data = {
        "info": {
            "title": "Installation Form",
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post("https://forms.googleapis.com/v1/forms", json=form_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return response.json()


@app.get("/get-forms")
def get_form_details(form_id, access_token):
    url = f"https://forms.googleapis.com/v1/forms/{form_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Returns the form details
    else:
        return response.json()  # Returns the error details


# @app.post("/update-forms")
# def batch_update_form(access_token, form_id):
#     url = f"https://forms.googleapis.com/v1/forms/{form_id}:batchUpdate"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     batch_update_data = {
#         "requests": [
#             {
#                 "createItem": {
#                     "item": {
#                         "title": "What is your favorite programming language?",
#                         "questionItem": {
#                             "question": {
#                                 "required": True,
#                                 "choiceQuestion": {
#                                     "type": "RADIO",
#                                     "options": [
#                                         {"value": "Python"},
#                                         {"value": "JavaScript"},
#                                         {"value": "Java"}
#                                     ],
#                                     "shuffle": False
#                                 }
#                             }
#                         }
#                     },
#                     "location": {
#                         "index": 0
#                     }
#                 }
#             },
#             {
#                 "createItem": {
#                     "item": {
#                         "title": "Business Name",
#                         "questionItem": {
#                             "question": {
#                                 "required": True,
#                                 "paragraph": True,
#                                 "choiceQuestion": {
#                                     "type": "TEXT",
#                                     "shuffle": False
#                                 }
#                             }
#                         }
#                     },
#                     "location": {
#                         "index": 0
#                     }
#                 }
#             }
#         ]
#     }
#
#     response = requests.post(url, headers=headers, json=batch_update_data)
#
#     if response.status_code == 200:
#         print("Form updated successfully!")
#         return response.json()
#     else:
#         print("Error:", response.status_code)
#         print(response.json())
#         return None

@app.post("/update-forms")
def batch_update_form(access_token: str, form_id: str):
    url = f"https://forms.googleapis.com/v1/forms/{form_id}:batchUpdate"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    batch_update_data = {
        "requests": [
            # Question 1: Paragraph Text
            {
                "createItem": {
                    "item": {
                        "title": "Business Name",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 0
                    }
                }
            },
            # Question 2: Multiple-choice
            {
                "createItem": {
                    "item": {
                        "title": "Do You Have An Internet Provider?",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {"value": "YES"},
                                        {"value": "NO"}
                                    ],
                                    "shuffle": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 1
                    }
                }
            },
        ]
    }

    response = requests.post(url, headers=headers, json=batch_update_data)

    if response.status_code == 200:
        print("Form updated successfully!")
        return response.json()
    else:
        print("Error:", response.status_code)
        print(response.json())
        return response.json()


@app.get("/form-response")
# def get_form_response(access_token, form_id, response_id):
#     url = f"https://forms.googleapis.com/v1/forms/{form_id}/responses/{response_id}"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json",
#     }
#
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         print("Form response retrieved successfully!")
#         return response.json()
#     else:
#         print(f"Error: {response.status_code}")
#         print(response.json())
#         return None
def get_form_responses(access_token: str, form_id: str, page_size: int = 100, page_token: str = None):
    """
    Retrieve all responses for a specific form.
    """
    url = f"https://forms.googleapis.com/v1/forms/{form_id}/responses"
    params = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        json_response = response.json()
        if "responses" in json_response:
            return {"responses": json_response["responses"]}
        else:
            return {"message": "No responses found for this form."}
    else:
        return {
            "error": response.status_code,
            "details": response.json(),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)