from locust import HttpUser, task, between
import json

class EmployeeUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
       
        login_data = {"username": "peter", "password": "peter123"}
        auth_url = "http://localhost:8001/token"
        response = self.client.post(auth_url, data=login_data)

        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.token = f"Bearer {token}"
        else:
            if self.environment.runner:
                self.environment.runner.quit()

    @task(6)
    def get_employees(self):
        if not hasattr(self, 'token'):
            return
        headers = {"Authorization": self.token}
        self.client.get("/employees/", headers=headers)

    @task(2)
    def create_employee(self):
        if not hasattr(self, 'token'):
            return
        headers = {"Authorization": self.token}

        import uuid
        emp_data = {
            "name": f"Load test emp {uuid.uuid4().hex[:6]}",
            "role": "Tester employee",
            "salary": 10000,
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com"
        }

        with self.client.post("/employees/", json=emp_data, headers=headers, catch_response=True) as response:
            if response.status_code != 200 and response.status_code != 201:
                response.failure(f"Failed with status {response.status_code}: {response.text}")
