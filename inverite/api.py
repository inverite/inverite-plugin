import requests
import logging
import os


ENVIRONMENT = os.environ.get(
    "INVERITE_ENVIRONMENT", 'sandbox')  # sandbox | live | www
APIKEY = os.environ.get('INVERITE_APIKEY', '')
HOSTNAME = "{}.inverite.com".format(ENVIRONMENT)
HEADERS = {
    "Auth": APIKEY,
    "Content-Type": "application/json"
}


def fetch_banks(guid):
    url = "https://{}/api/bank/list_available".format(HOSTNAME)
    result = requests.get(url, headers=HEADERS).json()
    if "errors" in result:
        raise ValueError("API stated error: {}".format(result["errors"]))
    if "banks" not in result:
        raise ValueError("missing banks")
    return result['banks']


def fetch_bankform(bankID):
    url = "https://{}/api/bank_form/{}".format(HOSTNAME, bankID)
    result = requests.get(url, headers=HEADERS) \
                     .json()
    if "errors" in result:
        raise ValueError("API stated error: {}".format(result["errors"]))
    if "fields" not in result:
        raise ValueError("missing fields")
    return result["fields"]


def session_start(guid, bankID, username,
                  password, branch=None, ip=None, user_agent=None):
    url = "https://{}/api/session_start/{}".format(HOSTNAME, guid)
    payload = {
        "username": username,
        "password": password,
        "bankID": int(bankID),
        "ip": ip,
        "useragent": user_agent,
    }
    if branch:
        payload["branch"] = branch
    logging.error(payload)
    return requests.post(url, headers=HEADERS, json=payload) \
                   .json()


def fetch_session_status(job_id):
    url = "https://{}/api/session_status/{}".format(
        HOSTNAME, job_id)
    return requests.get(url, headers=HEADERS) \
                   .json()


def provide_challenge_response(job_id, challenge_response):
    url = "https://{}/api/session_challenge_response/{}".format(
        HOSTNAME, job_id)
    payload = {"response": challenge_response}
    logging.error(payload)
    return requests.post(url, headers=HEADERS, json=payload) \
                   .json()
