import time
import requests
from config.settings import *

def send_public_message(
    message_text: str,
    roomName: str,
    classification: str = "UNCLASSIFIED//FOUO",
    domainId: str = "chatsurferxmppunclass",
    nickName: str = "Ferry Monitor",
):
    headers = {
        "Content-type": "application/json",
    }
    if TEST == "True":
        nickName = "Ferry Monitor (local)"
    message = {
        "classification": classification,
        "message": message_text.replace("**", ""),
        "domainId": domainId,
        "nickName": nickName,
        "roomName": roomName,
    }

    url = "https://" + CS_HOST + "/api/chatserver/message?api-key=" + CHATKEY

import os
import re

# Cache for the cleaned CA bundle path
CLEAN_CA_BUNDLE_PATH = None

def get_clean_ca_bundle(original_path):
    """
    Reads the CA bundle from original_path, extracts only the valid PEM 
    CERTIFICATE blocks, validates they look correct, and writes them to a 
    temp file. Returns the path to that temp file.
    
    This fixes issues where the CA bundle has extra text (like subject=...)
    at the start, which causes SSLError with [X509] PEM lib.
    """
    global CLEAN_CA_BUNDLE_PATH
    
    # If we already have a valid cleaned file, return it
    if CLEAN_CA_BUNDLE_PATH and os.path.exists(CLEAN_CA_BUNDLE_PATH):
        return CLEAN_CA_BUNDLE_PATH

    try:
        if not os.path.exists(original_path):
            print(f"WARNING: CA bundle path {original_path} does not exist.")
            return original_path

        with open(original_path, 'r') as f:
            content = f.read()

        # Regex to find all certificates
        # It looks for -----BEGIN CERTIFICATE----- ... -----END CERTIFICATE-----
        # flags=re.DOTALL matches across newlines
        certs = re.findall(r'(-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----)', content, re.DOTALL)

        if not certs:
            print(f"WARNING: No valid certificates found in {original_path}. Using original.")
            return original_path

        # print(f"INFO: Found {len(certs)} valid certificates in {original_path}. Creating cleaned bundle.")

        # Create a temp file
        # We use /tmp explicitly or let system decide. 
        # Since we might be in a container, /tmp is usually safe.
        clean_path = os.path.join("/tmp", "clean_dod_CA.pem")
        
        with open(clean_path, 'w') as f:
            for cert in certs:
                f.write(cert + "\n")
        
        CLEAN_CA_BUNDLE_PATH = clean_path
        return clean_path

    except Exception as e:
        print(f"ERROR: Failed to clean CA bundle: {e}. Fallback to original.")
        return original_path


def send_public_message(
    message_text: str,
    roomName: str,
    classification: str = "UNCLASSIFIED//FOUO",
    domainId: str = "chatsurferxmppunclass",
    nickName: str = "Ferry Monitor",
):
    headers = {
        "Content-type": "application/json",
    }
    if TEST == "True":
        nickName = "Ferry Monitor (local)"
    message = {
        "classification": classification,
        "message": message_text.replace("**", ""),
        "domainId": domainId,
        "nickName": nickName,
        "roomName": roomName,
    }

    url = "https://" + CS_HOST + "/api/chatserver/message?api-key=" + CHATKEY

    # Use cleaned CA bundle
    verify_path = get_clean_ca_bundle(CA_BUNDLE_PATH)

    try:
        send = requests.post(
            url,
            cert=(CERT_PATH, KEY_PATH),
            verify=verify_path,
            headers=headers,
            json=message,
        )
        # Uncomment to debug successful sends if needed
        # print(f"Response from ChatSurfer send public message: {send}")
    except Exception as e:
        print(f"ERROR: Failed to send public message: {e}")


