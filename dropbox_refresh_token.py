import dropbox
from pathlib import Path
import requests
import streamlit as st
import os


# def get_tokens(app_key, app_secret, authorization_code):
#     url = "https://api.dropbox.com/oauth2/token"
#     data = {
#         "code": authorization_code,
#         "grant_type": "authorization_code",
#         "client_id": app_key,
#         "client_secret": app_secret,
#     }
#     response = requests.post(url, data=data)
#     if response.status_code == 200:
#         return response.json()  # Contains access_token, refresh_token, and more
#     else:
#         raise Exception(f"Failed to get tokens: {response.text}")

# tokens = get_tokens(APP_KEY, APP_SECRET, AUTHORIZATION_CODE)
# print(tokens)

def get_access_token(app_key, app_secret, refresh_token):
    import requests
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": app_key,
        "client_secret": app_secret
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to refresh access token: {response.text}")