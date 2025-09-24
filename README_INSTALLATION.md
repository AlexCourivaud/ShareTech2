# ShareTech2

Side project ShareTech for AI ACADEMY

Sur Terminal powershell et commande docker :

Création des fichiers back :

docker run --rm -v "${PWD}/backend:/app" -w /app python:3.12 sh -c "pip install django && django-admin startproject sharetech && cd sharetech && python manage.py startapp accounts && python manage.py startapp core && python manage.py startapp notifications && python manage.py startapp attachments"

Création des fichiers front :

docker run --rm -v "${PWD}/frontend:/app" -w /app node:22-alpine sh -c "npx create-react-app . --template minimal"


lancement test docker : 
docker-compose up --build






Note : nettoyage docker :

- Arrêter tous les containers en cours

docker-compose down

- Supprimer containers, réseaux, volumes et images

docker-compose down -v

- Nettoyage complet du système Docker

docker system prune -a -f
