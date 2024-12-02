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
        f"&scope={SCOPES}"
        f"&access_type=offline"
    )
    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
    """
    Step 2: Handle the OAuth 2.0 callback from Google.
    Exchange the authorization code for an access token.
    """
    wishes = "WELCOME TO THE TECHIES WORLD"


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
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")  # Save this for long-term access
        return JSONResponse(
            content={
                "PageData": wishes,
                "message": "Access token obtained successfully!",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
    else:
        return JSONResponse(
            content={"error": token_response.json()}, status_code=token_response.status_code
        )


@app.get("/get-emails")
async def get_emails(access_token: str):
    """
    Step 3: Use the access token to fetch Gmail messages.
    """
    gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    response = requests.get(
        gmail_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code == 200:
        return JSONResponse(content=response.json())  # List of Gmail messages
    else:
        return JSONResponse(
            content={"error": response.json()}, status_code=response.status_code
        )


@app.get("/refresh-token")
def refresh_access_token(refresh_token, client_id, client_secret):
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, data=payload)
    return response.json()

# # Use your refresh token and client details
# refresh_token = "1//0g7pLRurR7ySwCgYIARAAGBASNwF-L9Ir86NlrVi93-Cm6KhDDpsGed-PdHfKLFihXMaGnIjHoyfgsyZ2B5yyMHkkWevSGKDDfc0"
# client_id = "1061361896514-k20p2tb5lg1rsekh2k51265ci7b8b3gq.apps.googleusercontent.com"
# client_secret = "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"
# new_tokens = refresh_access_token(refresh_token, client_id, client_secret)
# print(new_tokens)  # This will contain the new access token

# def get_gmail_messages(access_token):
#     url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return response.json()  # Return error details if something goes wrong
#
# # Use the access token you received
# access_token = "ya29.a0AeDClZAceuRw0Pl5dQydNvBY6FAE7FIBiB0UlRqYlEZqW7MwNP8QXpWP-EmxgGMOKs9hYRZQhOzMYm8LvQ3PX6z1cXvOUp4hC7zLkuZoujwlJIO7OrLiQN08Im5y_rzprA03S4g-hje9gWbEuxnyIzDBYkb9Ce_dz-VU28gDaCgYKAYwSARISFQHGX2Mi0_8ghDEkfw9YC2q9gFg_jg0175"
# messages = get_gmail_messages(access_token)
# print(messages)

import requests

@app.get("/user-details")
def get_gmail_profile(access_token):
    url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"  # Use 'me' for the current user
    headers = {
        "Authorization": f"Bearer {access_token}"  # Pass the access token in the header
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Profile data
    else:
        return response.json()  # Error details


# # Example usage
# access_token = "ya29.your_access_token_here"  # Replace with your actual access token
# profile = get_gmail_profile(access_token)
# print(profile)

@app.post("/create-form")
def exchange_code_for_token(auth_code):
    token_url = TOKEN_URI
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    redirect_uri = REDIRECT_URI

    data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json()  # Returns access and refresh tokens
    else:
        return response.json()  # Returns error details

# # Example usage
# access_token = "ya29.a0AeDClZD0xTPYYJsccMuBdXYNMMq3Qmtb8vcTDRkA9AGyIg-HL9KO9aYVsOKRZ9rjfQmQ2nQclrf_glDcnJ_0vrzJiSvsb1acl0Mo4ULAcU1TFApwH2k8vfbdy7xB-6BJGx7VcXUg4uqgN6tEgYteS0a_JZtrX6dLlb8aCgYKAc8SARISFQHGX2MiW-OQu9RQ_nBpr0kHp1nMzA0170"  # Replace with a valid access token
# form_title = "Feedback Form"
# form_description = "A form to collect user feedback."
# response = create_google_form(access_token, form_title, form_description)
# print(response)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
