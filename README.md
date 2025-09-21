# ShareTech2
Side project ShareTech for AI ACADEMY 

Via Powershell :

installation des app djangop via docker :
docker run --rm -v "${PWD}/backend:/app" -w /app python:3.12 sh -c "pip install django && django-admin startproject sharetech . && python manage.py startapp accounts && python manage.py startapp core"

Installation de react :
docker run --rm -v "${PWD}/frontend:/app" -w /app node:22-alpine sh -c "npx create-react-app . --template minimal"