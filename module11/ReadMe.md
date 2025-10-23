Commands to start all apps
CD into the module11 folder

uvicorn employee_service.main:app --reload --port 8000
uvicorn auth_service.auth_main:app --reload --port 8001
uvicorn notification_service.main:app --reload --port 8002