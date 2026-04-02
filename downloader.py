import requests
import json

#example base_url  = "https://dirict_name.infinitecampus.org/campus"
session = requests.Session()

def fetch_grades(base_url,usr, pwd, loc):
    payload = {
        "username": usr,
        "password": pwd,
        "appName": loc,
        "portalUrl": f"portal/students/{loc}.jsp",
        "url": "nav-wrapper",
        "lang": "en",
        "portalLoginPage": "students"
    }

    login_res = session.post(f"{base_url}/verify.jsp", data=payload)

    if login_res.status_code != 200:
        return f"Login request failed: HTTP {login_res.status_code}"

    res = session.get(f"{BASE_URL}/resources/portal/grades")

    try:
        data = res.json()
        if "errors" in data:
            return f"Login failed: {data['errors'][0]['message']}"
        with open("grades.json", "w", encoding="utf-8") as grades:
            json.dump(data, grades, indent=2)
        return "grades.json"
    except Exception as e:
        return f"Failed: {e}, Response: {res.text[:200]}"
