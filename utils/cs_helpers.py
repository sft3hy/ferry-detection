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

    # Debug certs
    import os
    print("DEBUG: Checking certificate files:")
    for name, path in [("CERT_PATH", CERT_PATH), ("KEY_PATH", KEY_PATH), ("CA_BUNDLE_PATH", CA_BUNDLE_PATH)]:
        if os.path.exists(path):
            try:
                size = os.path.getsize(path)
                with open(path, 'r') as f:
                    content = f.read(50)  # Read first 50 chars
                    clean_content = content.replace('\n', '\\n')
                print(f"  {name}: {path} EXISTS (Size: {size} bytes). Start: '{clean_content}'")
            except Exception as e:
                print(f"  {name}: {path} EXISTS but could not read: {e}")
        else:
            print(f"  {name}: {path} DOES NOT EXIST")
            dirname = os.path.dirname(path)
            if os.path.exists(dirname):
                print(f"    Directory {dirname} contents: {os.listdir(dirname)}")
            else:
                print(f"    Directory {dirname} DOES NOT EXIST")


    send = requests.post(
        url,
        cert=(CERT_PATH, KEY_PATH),
        verify=CA_BUNDLE_PATH,
        headers=headers,
        json=message,
    )
    print(f"Response from ChatSurfer send public message: {send}")

