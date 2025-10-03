import requests, os, json
from requests.auth import HTTPBasicAuth
from app.sql.departments_db import add_departments_table

def get_departments():
    i = 1
    departments = []
    key = os.environ["FSKEY"]

    while True:
        url = f"https://eastwest.freshservice.com/api/v2/departments?page={i}"

        response = requests.get(url, auth=HTTPBasicAuth(key, 'X'))
        
        group = response.json()["departments"]
        if not group:
            break

        for department in group:
            departments.append(department)

        i += 1

    #Letting this function handle storing any new departments to the departments table. Don't want to fill up main() with too much and this won't be running all the time. Only every once in a while to make sure departments are up-to-date.
    for department in departments:
        add_departments_table(department)
        departments = []
