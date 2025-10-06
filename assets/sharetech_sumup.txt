# ShareTech - Architecture du Projet
---
## 1. Description du Projet

**ShareTech** est une plateforme collaborative développée pour l'entreprise Memory. Elle centralise la documentation et la gestion de tâches pour les équipes de développement.

### Objectifs
- Centraliser les connaissances dans un espace unique
- Faciliter le suivi des tâches et leur assignation
- Améliorer la collaboration entre développeurs
- Tracer l'historique des décisions
### Fonctionnalités Principales

**Partage de Connaissances**
- Création et gestion de notes
- Système de commentaires hiérarchiques (max 5 niveaux)
- Classification par tags (max 10 par note)
- Recherche full-text dans titres et contenus
- Gestion de fichiers joints (max 100MB)

**Gestion de Tâches**
- Création et assignation de tâches aux membres
- Suivi d'avancement avec statuts (à faire → en cours → en test → terminée)
- Gestion des priorités (basse, normale, haute, urgente) et échéances
- Tableau de bord Kanban
- Notifications automatiques sur changements

**Système Collaboratif**
- Gestion de projets multi-membres avec rôles
- Système de permissions hiérarchique (Junior → Senior → Lead → Admin)
- Notifications in-app avec préférences
- Historique complet des actions

---

## 2. Vue d'Ensemble

### Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Interface utilisateur                                 │
│  - Context API (état global)                            │
│  - Communication API REST                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ HTTP / REST API
┌─────────────────────────────────────────────────────────┐
│              Backend (Django REST Framework)             │
│  - Logique métier                                       │
│  - Authentification & Permissions                       │
│  - API REST                                             │
│  - User Django par défaut + UserProfile (OneToOne)      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ ORM Django
┌─────────────────────────────────────────────────────────┐
│              Base de Données (MariaDB)                   │
│  - 11 tables principales                                │
│  - Relations & Contraintes d'intégrité                  │
└─────────────────────────────────────────────────────────┘
```

### Système de Rôles et Permissions

**Hiérarchie** : Admin > Lead Developer > Senior Developer > Junior Developer

| Rôle | Permissions principales |
|------|-------------------------|
| **Junior** | Consulter projets, créer notes, commenter, voir tâches assignées |
| **Senior** | Junior + modifier toutes les notes, consulter toutes les tâches |
| **Lead** | Senior + gérer projets, créer/assigner tâches, gérer membres |
| **Admin** | Lead + gérer utilisateurs, supprimer projets, configuration globale |

---

## 3. Stack Technique

### Backend
- **Framework** : Django 5.0.1
- **API REST** : Django REST Framework 3.14.0
- **Langage** : Python 3.12
- **Dépendances clés** :
  - `django-cors-headers` - Support CORS
  - `mysqlclient` - Connecteur MariaDB
  - `python-decouple` - Gestion configuration
  - `Pillow` - Traitement d'images
  - `django-filter` - Filtres API

### Frontend
- **Framework** : React 18.x
- **Langage** : JavaScript ES6+
- **Bibliothèques** :
  - `react-router-dom` - Routage
  - `axios` - Client HTTP
  - Context API - Gestion d'état global

### Base de Données
- **SGBD** : MariaDB 10.6
- **Moteur** : InnoDB (transactions ACID)
- **Collation** : utf8mb4_unicode_ci

### Infrastructure
- **Conteneurisation** : Docker 28.4.0 + Docker Compose v2.39.4-desktop.1
- **Services** :
  - `db` : MariaDB (port 3306)
  - `backend` : Django (port 8000)
  - `frontend` : React (port 3000)

  ### autres 
  **os** : Windows 11
   **ide** : VSCODE
   **terminal** : powershell 
   **Authentification** : Sessions Django par défaut
   **Gestion utilisateurs** : User Django par défaut + UserProfile (OneToOne) avec rôles


---

## 4. Schéma de Base de Données

### 4.1 Table USER - Utilisateurs

```
USER (auth_user - Table Django par défaut)
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── username              VARCHAR(150) UNIQUE NOT NULL
├── email                 VARCHAR(254) NOT NULL
├── password              VARCHAR(128) NOT NULL  (hash bcrypt)
├── first_name            VARCHAR(150) NOT NULL
├── last_name             VARCHAR(150) NOT NULL
├── is_active             BOOLEAN DEFAULT TRUE
├── is_staff              BOOLEAN DEFAULT FALSE
├── is_superuser          BOOLEAN DEFAULT FALSE
├── date_joined           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
└── last_login            TIMESTAMP NULLIndex:

- idx_user_username (username)
- idx_user_email (email)
```

### 4.2 Table USER_PROFILE - Profils utilisateurs
```
USER_PROFILE
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── user_id               INTEGER UNIQUE NOT NULL → USER.id [CASCADE]
├── role                  ENUM('junior', 'senior', 'lead', 'admin') DEFAULT 'junior'
├── avatar_url            VARCHAR(255) NULL
└── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Index:

idx_userprofile_user (user_id)
idx_userprofile_role (role)
```

### 4.3 Table PROJECT - Projets

```
PROJECT
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── name                  VARCHAR(100) NOT NULL
├── description           TEXT NULL
├── status                ENUM('actif', 'archive', 'suspendu') DEFAULT 'actif'
├── created_by            INTEGER NOT NULL → USER.id [CASCADE]
├── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
└── updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

Index:
- idx_project_status (status)
- idx_project_created_by (created_by)
```

### 4.4 Table PROJECT_MEMBER - Membres de projet

```
PROJECT_MEMBER
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── project_id            INTEGER NOT NULL → PROJECT.id [CASCADE]
├── user_id               INTEGER NOT NULL → USER.id [CASCADE]
├── role_project          ENUM('member', 'contributor', 'maintainer') DEFAULT 'member'
└── joined_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Contraintes:
- UNIQUE(project_id, user_id)

Index:
- idx_project_member_project (project_id)
- idx_project_member_user (user_id)
```

### 4.5 Table NOTE - Notes

```
NOTE
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── title                 VARCHAR(200) NOT NULL
├── content               TEXT NOT NULL
├── excerpt               VARCHAR(500) NULL
├── status                ENUM('brouillon', 'publie', 'archive') DEFAULT 'brouillon'
├── priority              ENUM('basse', 'normale', 'haute') DEFAULT 'normale'
├── project_id            INTEGER NOT NULL → PROJECT.id [CASCADE]
├── author_id             INTEGER NOT NULL → USER.id [CASCADE]
├── view_count            INTEGER DEFAULT 0
├── like_count            INTEGER DEFAULT 0
├── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
├── updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
└── published_at          TIMESTAMP NULL

Index:
- idx_note_project (project_id)
- idx_note_author (author_id)
- idx_note_status (status)
- idx_note_priority (priority)
- idx_note_project_status (project_id, status) [composite]
```

### 4.6 Table TASK - Tâches

```
TASK
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── title                 VARCHAR(200) NOT NULL
├── description           TEXT NULL
├── status                ENUM('a_faire', 'en_cours', 'en_test', 'terminee', 'annulee') DEFAULT 'a_faire'
├── priority              ENUM('basse', 'normale', 'haute', 'urgente') DEFAULT 'normale'
├── estimated_hours       DECIMAL(5,2) NULL
├── actual_hours          DECIMAL(5,2) NULL
├── due_date              DATE NULL
├── completed_date        DATE NULL
├── project_id            INTEGER NOT NULL → PROJECT.id [CASCADE]
├── assigned_to           INTEGER NULL → USER.id [SET NULL]
├── created_by            INTEGER NOT NULL → USER.id [CASCADE]
├── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
└── updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

Index:
- idx_task_project (project_id)
- idx_task_assigned (assigned_to)
- idx_task_status (status)
- idx_task_priority (priority)
- idx_task_due_date (due_date)
- idx_task_project_assigned (project_id, assigned_to) [composite]
- idx_task_status_due (status, due_date) [composite]
```

### 4.7 Table TAG - Étiquettes

```
TAG
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── name                  VARCHAR(50) UNIQUE NOT NULL
├── color                 VARCHAR(7) DEFAULT '#6b7280'
├── description           VARCHAR(200) NULL
├── usage_count           INTEGER DEFAULT 0
└── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Index:
- idx_tag_usage (usage_count)
```

### 4.8 Table NOTE_TAG - Classification notes (N:M)

```
NOTE_TAG
├── note_id               INTEGER NOT NULL → NOTE.id [CASCADE]
├── tag_id                INTEGER NOT NULL → TAG.id [CASCADE]
└── assigned_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP

PRIMARY KEY (note_id, tag_id)
```

### 4.9 Table TASK_TAG - Classification tâches (N:M)

```
TASK_TAG
├── task_id               INTEGER NOT NULL → TASK.id [CASCADE]
├── tag_id                INTEGER NOT NULL → TAG.id [CASCADE]
└── assigned_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP

PRIMARY KEY (task_id, tag_id)
```

### 4.10 Table COMMENT - Commentaires

```
COMMENT
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── content               TEXT NOT NULL
├── note_id               INTEGER NOT NULL → NOTE.id [CASCADE]
├── author_id             INTEGER NOT NULL → USER.id [CASCADE]
├── parent_comment_id     INTEGER NULL → COMMENT.id [CASCADE]
├── is_edited             BOOLEAN DEFAULT FALSE
├── like_count            INTEGER DEFAULT 0
├── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
└── updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

Index:
- idx_comment_note (note_id)
- idx_comment_author (author_id)
- idx_comment_parent (parent_comment_id)
```

### 4.11 Table ATTACHMENT - Fichiers joints

```
ATTACHMENT
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── original_name         VARCHAR(255) NOT NULL
├── stored_name           VARCHAR(255) NOT NULL
├── file_path             VARCHAR(500) NOT NULL
├── file_size             INTEGER NOT NULL
├── mime_type             VARCHAR(100) NOT NULL
├── file_hash             VARCHAR(64) NULL
├── note_id               INTEGER NULL → NOTE.id [CASCADE]
├── comment_id            INTEGER NULL → COMMENT.id [CASCADE]
├── uploaded_by           INTEGER NOT NULL → USER.id [CASCADE]
└── upload_date           TIMESTAMP DEFAULT CURRENT_TIMESTAMP

Contraintes:
- CHECK (note_id IS NOT NULL OR comment_id IS NOT NULL)

Index:
- idx_attachment_note (note_id)
- idx_attachment_comment (comment_id)
- idx_attachment_uploaded_by (uploaded_by)
```

### 4.12 Table NOTIFICATION - Notifications

```
NOTIFICATION
├── id                    INTEGER PRIMARY KEY AUTO_INCREMENT
├── type                  ENUM('note_created', 'note_updated', 'task_assigned', 
│                              'task_completed', 'comment_added', 'mention', 
│                              'project_invitation') NOT NULL
├── title                 VARCHAR(200) NOT NULL
├── message               TEXT NOT NULL
├── user_id               INTEGER NOT NULL → USER.id [CASCADE]
├── related_note_id       INTEGER NULL → NOTE.id [SET NULL]
├── related_task_id       INTEGER NULL → TASK.id [SET NULL]
├── related_comment_id    INTEGER NULL → COMMENT.id [SET NULL]
├── related_project_id    INTEGER NULL → PROJECT.id [SET NULL]
├── triggered_by          INTEGER NULL → USER.id [SET NULL]
├── is_read               BOOLEAN DEFAULT FALSE
├── read_at               TIMESTAMP NULL
├── created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
└── expires_at            TIMESTAMP NULL

Index:
- idx_notification_user (user_id)
- idx_notification_type (type)
- idx_notification_read (is_read)
- idx_notification_user_unread (user_id, is_read) [composite]
```

### 4.13 Schéma Relationnel Global

```
USER (1,1) ←──has_profile──→ USER_PROFILE (1,1)
USER (1,n) ──creates──→ PROJECT (1,1)
USER (1,n) ──belongs_to──→ PROJECT (0,n) [via PROJECT_MEMBER]
USER (1,n) ──authors──→ NOTE (1,1)
USER (0,1) ──assigned_to──→ TASK (1,n)
USER (1,n) ──creates──→ TASK (1,1)
USER (1,n) ──authors──→ COMMENT (1,1)
USER (1,n) ──uploads──→ ATTACHMENT (1,1)
USER (1,n) ──receives──→ NOTIFICATION (1,1)

PROJECT (1,n) ──contains──> NOTE (1,1)
PROJECT (1,n) ──contains──> TASK (1,1)

NOTE (1,n) ──has──> COMMENT (0,n)
NOTE (1,n) ──has──> ATTACHMENT (0,n)
NOTE (0,n) ──classified_by──> TAG (0,n) [via NOTE_TAG]

TASK (0,n) ──classified_by──> TAG (0,n) [via TASK_TAG]

COMMENT (0,1) ──replies_to──> COMMENT (0,n) [self-referencing]
COMMENT (1,n) ──has──> ATTACHMENT (0,n)
```

### 4.14 Règles de Suppression (ON DELETE)

**CASCADE** - Suppression en cascade :
- USER → USER_PROFILE, PROJECT, NOTE, TASK, COMMENT, ATTACHMENT, NOTIFICATION, PROJECT_MEMBER
- PROJECT → NOTE, TASK, PROJECT_MEMBER
- NOTE → COMMENT, ATTACHMENT, NOTE_TAG
- TASK → TASK_TAG
- TAG → NOTE_TAG, TASK_TAG
- COMMENT → COMMENT (replies), ATTACHMENT

**SET NULL** - Mise à NULL :
- USER → TASK.assigned_to
- NOTE/TASK/COMMENT/PROJECT → NOTIFICATION (related_*)
- USER → NOTIFICATION.triggered_by

---

## 5. Structure du Projet

### 5.1 Backend Django (Architecture Feature-Based)

```
backend/
├── sharetech/                  # Configuration Django principale
│   ├── __init__.py
│   ├── settings.py             # Configuration globale
│   ├── urls.py                 # Routage principal
│   └── wsgi.py                 # Point d'entrée WSGI
│
├── accounts/                   # Feature #1 - Authentification & Utilisateurs
│   ├── models.py               # UserProfile (OneToOne avec User Django)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── projects/                   # Feature #2 - Projets & Membres
│   ├── models.py               # Project, ProjectMember
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── tags/                       # Feature #3 - Tags (transversal)
│   ├── models.py               # Tag
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── notes/                      # Feature #4 - Notes
│   ├── models.py               # Note, NoteTag
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   ├── services.py             # Versioning, search
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── tasks/                      # Feature #5 - Tâches
│   ├── models.py               # Task, TaskTag
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   ├── services.py             # Assignation
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── comments/                   # Feature #6 - Commentaires
│   ├── models.py               # Comment
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── services.py             # Hiérarchie
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── notifications/              # Feature #7 - Notifications
│   ├── models.py               # Notification
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py             # Création auto
│   ├── signals.py              # Django signals
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── attachments/                # Feature #8 - Fichiers
│   ├── models.py               # Attachment
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py             # Upload sécurisé
│   ├── validators.py
│   ├── storage.py
│   ├── admin.py
│   ├── tests/
│   └── migrations/
│
├── requirements.txt            # Dépendances Python
├── Dockerfile
└── manage.py                   # CLI Django
```

### 5.2 Frontend React

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── components/             # Composants réutilisables
│   │   ├── common/             # Boutons, inputs, modals, cards
│   │   ├── auth/               # LoginForm, PrivateRoute
│   │   ├── projects/           # ProjectCard, ProjectList, ProjectForm
│   │   ├── notes/              # NoteCard, NoteEditor, NoteList
│   │   ├── tasks/              # TaskCard, TaskBoard, TaskForm
│   │   ├── comments/           # CommentItem, CommentThread
│   │   ├── tags/               # TagBadge, TagSelector
│   │   ├── notifications/      # NotificationBell, NotificationList
│   │   └── navigation/         # Header, Sidebar, Navbar
│   │
│   ├── contexts/               # Context API (état global)
│   │   ├── AuthContext.js      # Utilisateur connecté
│   │   ├── ProjectContext.js   # Projets et projet actuel
│   │   ├── TaskContext.js      # Tâches par statut
│   │   └── NotificationContext.js  # Notifications
│   │
│   ├── services/               # Services API (Axios)
│   │   ├── apiConfig.js        # Configuration Axios
│   │   ├── authService.js
│   │   ├── projectService.js
│   │   ├── noteService.js
│   │   ├── taskService.js
│   │   ├── commentService.js
│   │   ├── tagService.js
│   │   ├── notificationService.js
│   │   └── attachmentService.js
│   │
│   ├── pages/                  # Pages principales
│   │   ├── LoginPage.js
│   │   ├── Dashboard.js
│   │   ├── ProjectListPage.js
│   │   ├── ProjectDetailPage.js
│   │   ├── NoteDetailPage.js
│   │   ├── NoteEditorPage.js
│   │   ├── TaskBoardPage.js
│   │   ├── ProfilePage.js
│   │   └── NotFoundPage.js
│   │
│   ├── utils/                  # Utilitaires
│   │   ├── constants.js        # Constantes (rôles, statuts)
│   │   ├── helpers.js
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   └── permissions.js
│   │
│   ├── styles/                 # Styles CSS
│   │   ├── App.css
│   │   ├── variables.css
│   │   └── components/
│   │
│   ├── App.js                  # Composant racine + routing
│   └── index.js                # Point d'entrée
│
├── package.json
├── Dockerfile
└── .gitignore
```

---

## 6. Résumé de l'Organisation des Données

### 6.1 Backend - Features Django

| Feature | Responsabilité | Models | Priorité |
|---------|---------------|--------|----------|
| **accounts** | Authentification et gestion utilisateurs | UserProfile |  #1 ESSENTIEL |
| **projects** | Projets collaboratifs et membres | Project, ProjectMember |  #2 ESSENTIEL |
| **tags** | Tags partagés pour classification | Tag |  #3 TRANSVERSAL |
| **notes** | Notes | Note, NoteTag |  #4 CORE |
| **tasks** | Tâches avec assignation et suivi | Task, TaskTag |  #5 CORE |
| **comments** | Commentaires hiérarchiques sur notes | Comment | #6 ENHANCEMENT |
| **notifications** | Notifications automatiques in-app | Notification | #7 ENHANCEMENT |
| **attachments** | Upload et gestion de fichiers | Attachment | #8 ENHANCEMENT |

### 6.2 Frontend - Organisation par Type

**Contexts (État Global)**
- `AuthContext` : Gestion utilisateur connecté, login/logout
- `ProjectContext` : Liste projets et projet actuel sélectionné
- `TaskContext` : Tâches organisées par statut (Kanban)
- `NotificationContext` : Notifications + compteur non lues

**Services API**
- Un service par feature backend
- Communication HTTP via Axios
- Gestion centralisée des erreurs et CSRF tokens

**Pages Principales**
- `LoginPage` : Authentification
- `Dashboard` : Vue d'ensemble personnelle (tâches, notifications, activité)
- `ProjectListPage` : Liste des projets accessibles
- `ProjectDetailPage` : Détail projet avec tabs (notes, tâches, membres)
- `NoteDetailPage` : Affichage note avec commentaires
- `NoteEditorPage` : Création/édition
- `TaskBoardPage` : Tableau Kanban des tâches
- `ProfilePage` : Profil et paramètres utilisateur

---

### sécurité 

variable d'environnement stocké dans le fichier .env
# === DJANGO SETTINGS ===
SECRET_KEY=ton_secret_key_super_long_et_aleatoire_ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# === DATABASE (MariaDB) ===
DB_NAME=sharetech_db
DB_USER=sharetech_user
DB_PASSWORD=ton_mot_de_passe_securise
DB_HOST=db
DB_PORT=3306

# === CORS (Communication Frontend/Backend) ===
CORS_ALLOWED_ORIGINS=http://localhost:3000

# === MEDIA FILES (fichiers uploadés) ===
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
organisé par type d'entité et eviter collision

### divers : 

Nous utiliserons github pour stocker le fichier mais pas besoin d'en parler

Migration créés par django automatiquement

Systeme de seeding Django fixtures (JSON)

backup à voir lorsque l'on fera le deploiement

le systeme de route sera fait au fur et a mesure et logique et ordonné par besoin de détailler ce point.

gestion des formulaire sera fait par react natif

### TESTS 

implémentation de tests progressif au fur et a mesure du développement

Tests Unitaires : Fonctions isolées, validations, propriétés modèles
Tests d'Intégration : Endpoints API complets (requête → DB → réponse)
Tests de Permissions : Vérifier accès par rôle pour chaque action
 - outils a utiliser
Backend (Django)
pytest : Framework de test moderne pour Python.
pytest-django : Plugin pour intégrer Django avec pytest.
pytest-cov : Mesure de la couverture de code.
factory_boy : Génération de données de test (fixtures).
django-test-plus : Extensions utiles pour les tests Django.
black : Formatteur de code Python.
flake8 : Linter pour détecter les erreurs de style et de syntaxe.
isort : Trie les imports Python.

Frontend (React)
Jest : Framework de test pour JavaScript/React.
@testing-library/react : Utilitaires pour tester les composants React.
react-test-renderer : Pour tester le rendu des composants.
eslint : Linter pour JavaScript/React.
prettier : Formatteur de code pour une cohérence visuelle.

### documentation API
génération par Django automatiquement


Bonjour Claude,

Je développe ShareTech, une application web collaborative pour la gestion 
de documentation et de tâches.

Ma documentation complète est dans le fichier sharetech_sumup.txt joint.

Après l'avoir lue, confirme ta compréhension de l'architecture globale 
et propose-moi le plan détaillé pour démarrer le développement.