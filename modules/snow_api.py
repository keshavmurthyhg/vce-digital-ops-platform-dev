import requests

def fetch_incident(incident_number):
    url = f"https://your-instance.service-now.com/api/now/table/incident?sysparm_query=number={incident_number}"

    headers = {"Accept": "application/json"}

    response = requests.get(url, auth=("username", "password"), headers=headers)

    if response.status_code == 200:
        result = response.json()["result"]
        if result:
            return result[0]
    return None
