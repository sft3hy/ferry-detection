import time
import requests
from config.settings import *

def send_public_message(
    message_text: str,
    roomName: str,
    session_id: str,
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
    cook = {"SESSION": session_id}

    url = "https://" + CS_HOST + "/api/chatserver/message?api-key=" + CHATKEY

    send = requests.post(
        url,
        cert=(CERT_PATH, KEY_PATH),
        verify=CA_BUNDLE_PATH,
        headers=headers,
        json=message,
        cookies=cook,
    )
    print(f"Response from ChatSurfer send public message: {send}")


def session_request():
    # clear_sessions()
    print("session expired, creating new session")
    url = "https://" + CS_HOST + "/api/auth/newsession"
    headers = {
        "Content-type": "application/json",
    }
    json_data = {
        "apiKey": CHATKEY,
    }
    session_response = requests.post(
        url,
        cert=(CERT_PATH, KEY_PATH),
        headers=headers,
        json=json_data,
        verify=CA_BUNDLE_PATH,
    )
    tries = 5
    while session_response.status_code > 204 and tries > 0:
        if (
            "Set-Cookie" in session_response.headers
            and session_response.headers["Set-Cookie"].split(";")[0] != "SESSION="
        ):
            break
        else:
            session_response = requests.post(
                url,
                cert=(CERT_PATH, KEY_PATH),
                headers=headers,
                json=json_data,
                verify=CA_BUNDLE_PATH,
            )
            time.sleep(1)
            tries -= 1
    session_id = session_response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    with open("session_created.txt", "w") as f:
        f.write(f"{time.time()+(SESSION_EXPIRATION_TIME)}separator1234{session_id}")
    print("got session:", session_id)
    return session_id


def create_session():
    with open("session_created.txt", "r") as f:
        text = f.read()
    if "separator1234" in text:
        info = text.split("separator1234")
        if time.time() > float(info[0]) or info[1] == "":
            session_id = session_request()
        else:
            print("using existing session:", info[1])
            session_id = info[1]
    else:
        session_id = session_request()
    return session_id


def clear_sessions():
    url = "https://" + CS_HOST + "/api/auth/clearsessions?api-key=" + CHATKEY
    clear = requests.post(url, cert=(CERT_PATH, KEY_PATH), verify=CA_BUNDLE_PATH)
    tries = 5
    while clear.status_code > 204 and tries > 0:
        clear = requests.post(url, cert=(CERT_PATH, KEY_PATH), verify=CA_BUNDLE_PATH)
        time.sleep(1)
        tries -= 1