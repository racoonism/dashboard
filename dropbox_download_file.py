import dropbox
import io
import streamlit as st
import pandas as pd

def download_from_dropbox(file_path, local_path, access_token):
    dbx = dropbox.Dropbox(access_token)
    metadata, res = dbx.files_download(file_path)
    with open(local_path, "wb") as f:
        f.write(res.content)

def download_from_dropbox_IO(file_path, access_token):

    dbx = dropbox.Dropbox(access_token)
    try:
        # Download the file
        metadata, res = dbx.files_download(file_path)
        # Read the content into a DataFrame
        data = pd.read_csv(io.BytesIO(res.content))
        return data
    except dropbox.exceptions.ApiError as e:
        st.error(f"Failed to fetch file from Dropbox: {e}")
        return None


# Example usage
# ACCESS_TOKEN = "your_dropbox_access_token"
# DROPBOX_FILE_PATH = "/example_file.txt"
# LOCAL_PATH = "example_file.txt"


