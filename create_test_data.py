#!/usr/bin/env python
"""
Script de création de données de test pour ShareTech
Crée des users, projets et membres pour tester l'application
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharetech.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from projects.models import Project, ProjectMember

def create_test_data():
    print("Début de la création des données de test...\n")

    # ===== 1. RÉCUPÉRATION DU SUPERUSER =====
    try:
        superuser = User.objects.get(username='superuser')
        print(f"Superuser récupéré: {superuser.username} (role: {superuser.profile.get_role_display()})")
    except User.DoesNotExist:
        print("Superuser 'superuser' introuvable. Veuillez le créer d'abord.")
        return

    # ===== 2. CRÉATION DES USERS =====
    print("\n Création des utilisateurs...")

    # Créer junioruser1
    if User.objects.filter(username='junioruser1').exists():
        junioruser1 = User.objects.get(username='junioruser1')
        print(f"  junioruser1 existe déjà")
    else:
        junioruser1 = User.objects.create_user(
            username='junioruser1',
            email='junioruser1@sharetech.com',
            password='kirua2604'
        )
        # Le signal crée automatiquement le UserProfile avec role='junior' par défaut
        # Mais on va s'assurer qu'il a le bon rôle
        junioruser1.profile.role = 'junior'
        junioruser1.profile.save()
        print(f"User créé: {junioruser1.username} (role: {junioruser1.profile.get_role_display()})")

    # Créer leadtest1
    if User.objects.filter(username='leadtest1').exists():
        leadtest1 = User.objects.get(username='leadtest1')
        print(f"  leadtest1 existe déjà")
    else:
        leadtest1 = User.objects.create_user(
            username='leadtest1',
            email='leadtest1@sharetech.com',
            password='kirua2604'
        )
        # Changer le rôle en Lead
        leadtest1.profile.role = 'lead'
        leadtest1.profile.save()
        print(f" User créé: {leadtest1.username} (role: {leadtest1.profile.get_role_display()})")

    # ===== 3. CRÉATION DES PROJETS =====
    print("\n Création des projets...")

    # Projet 1: projettest1
    if Project.objects.filter(name='projettest1').exists():
        projettest1 = Project.objects.get(name='projettest1')
        print(f"  Projet 'projettest1' existe déjà")
    else:
        projettest1 = Project.objects.create(
            name='projettest1',
            description='ceci est le contenu du projet 1 de test',
            created_by=superuser
        )
        print(f" Projet créé: {projettest1.name}")

    # Projet 2: Projettest2
    if Project.objects.filter(name='Projettest2').exists():
        projettest2 = Project.objects.get(name='Projettest2')
        print(f"  Projet 'Projettest2' existe déjà")
    else:
        projettest2 = Project.objects.create(
            name='Projettest2',
            description='ceci est le second projet ou il y a 2 personne dedans avec un lorem ipsim',
            created_by=superuser
        )
        print(f" Projet créé: {projettest2.name}")

    # Projet 3: ProjetFULLtest3
    if Project.objects.filter(name='ProjetFULLtest3').exists():
        projetfullt3 = Project.objects.get(name='ProjetFULLtest3')
        print(f"  Projet 'ProjetFULLtest3' existe déjà")
    else:
        projetfullt3 = Project.objects.create(
            name='ProjetFULLtest3',
            description='ceci sera le stress test des projets !',
            created_by=superuser
        )
        print(f" Projet créé: {projetfullt3.name}")

    # ===== 4. AJOUT DES MEMBRES AUX PROJETS =====
    print("\n👥 Ajout des membres aux projets...")

    # Projettest2: superuser, junioruser1, leadtest1
    members_p2 = [superuser, junioruser1, leadtest1]
    for user in members_p2:
        if not ProjectMember.objects.filter(project=projettest2, user=user).exists():
            pm = ProjectMember.objects.create(project=projettest2, user=user)
            print(f" Membre ajouté: {pm}")
        else:
            print(f"  {user.username} est déjà membre de {projettest2.name}")

    # ProjetFULLtest3: superuser, leadtest1
    members_p3 = [superuser, leadtest1]
    for user in members_p3:
        if not ProjectMember.objects.filter(project=projetfullt3, user=user).exists():
            pm = ProjectMember.objects.create(project=projetfullt3, user=user)
            print(f" Membre ajouté: {pm}")
        else:
            print(f"  {user.username} est déjà membre de {projetfullt3.name}")

    # ===== 5. RÉSUMÉ =====
    print("\n" + "="*60)
    print(" RÉSUMÉ DE LA CRÉATION")
    print("="*60)

    print("\n UTILISATEURS:")
    print(f"  - superuser (Admin)")
    print(f"  - junioruser1 (Junior) - mdp: kirua2604")
    print(f"  - leadtest1 (Lead) - mdp: kirua2604")

    print("\n PROJETS:")
    print(f"  1. {projettest1.name}")
    print(f"     Description: {projettest1.description}")
    print(f"     Créé par: {projettest1.created_by.username}")
    print(f"     Membres: Aucun (juste le créateur)")

    print(f"\n  2. {projettest2.name}")
    print(f"     Description: {projettest2.description}")
    print(f"     Créé par: {projettest2.created_by.username}")
    members_2 = ProjectMember.objects.filter(project=projettest2)
    print(f"     Membres ({members_2.count()}): {', '.join([m.user.username for m in members_2])}")

    print(f"\n  3. {projetfullt3.name}")
    print(f"     Description: {projetfullt3.description}")
    print(f"     Créé par: {projetfullt3.created_by.username}")
    members_3 = ProjectMember.objects.filter(project=projetfullt3)
    print(f"     Membres ({members_3.count()}): {', '.join([m.user.username for m in members_3])}")

    print("\n Toutes les données de test ont été créées avec succès!")

if __name__ == '__main__':
    create_test_data()
