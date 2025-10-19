ShareTech - Plateforme Collaborative pour Développeurs de la société Memory

ShareTech est une plateforme web collaborative qui unifie le partage de connaissances techniques et la gestion de tâches pour les équipes de développement. Elle permet aux développeurs de centraliser leur documentation, gérer leurs projets et suivre l'avancement du travail dans un environnement unique.

- Fonctionnalités Principales

- Gestion de Notes Techniques : Création et partage de documentation avec support Markdown, coloration syntaxique et système de tags
- Gestion de Tâches : Tableau Kanban pour le suivi des tâches avec assignation, priorités et échéances
- Collaboration d'Équipe : Système de commentaires hiérarchiques, mentions et notifications temps réel
- Gestion des Permissions : 4 rôles hiérarchiques (Junior, Senior, Lead Developer, Admin)
- Recherche Avancée : Recherche full-text dans notes et tâches avec filtres avancés
- Gestion de Fichiers : Upload et gestion de pièces jointes (images, documents, code)

Stack Technique

- Backend : Django 5.0.1 + Django REST Framework 3.14.0
- Frontend : React 18.x avec Context API
- Base de Données : MariaDB 10.6
- Infrastructure : Docker + Docker Compose
- Architecture : API REST avec 20+ endpoints

Objectif

Réduire la dispersion entre outils de documentation et de gestion de projet en offrant une expérience unifiée qui améliore la productivité et facilite la capitalisation des connaissances techniques.




Starting a project : 



Lancer docker :

CheatSheet Docker :

Créer les containers : docker-compose up --build -d

Voir le statut des containers : docker-compose ps

lancer les migrations :
docker-compose exec backend python manage.py migrate

voir si des migrations sont en attente : 
docker-compose exec backend python manage.py showmigrations --plan