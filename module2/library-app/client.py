import json
import requests

BASE_URL = "http://localhost:8000/users"

# Add a new user
headers = {"Content-Type": "application/json"}
payload = {"name":"John123", "email":"john124@gmail.com"}

response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))
print("POST /users", response.status_code, response.json())

# Edit a user

user_id = response.json().get("id")
update_payload = {"name" : "John Snow", "email" : "Johnsnow123@gmail.com"}
put_url = f"{BASE_URL}/{user_id}"

response = requests.put(put_url, headers=headers, data=json.dumps(update_payload))
print("PUT /users/<id> =>", response.status_code, response.json())

# Handle 404/ wrong endpoint

wrong_url = "http://localhost:8000/unknown"
bad_response = requests.get(wrong_url)
print("Get /unknown => ", bad_response.status_code)
