# Openclassrooms P10 - Créez une API sécurisée RESTful en utilisant Django REST

Ce projet consiste à implémenter une API [Django Rest Framework](https://www.django-rest-framework.org/), pour mettre à disposition d'un service web les ressources suivantes :

* ```User``` : Définit les utilisateurs, avec leur âge, leur choix de consentement et leurs identifiant.

* ```Contributor``` : Définit les utilisateurs qui sont contributeurs d’un projet spécifique… Un utilisateur peut contribuer à plusieurs projets, et un projet peut avoir plusieurs contributeurs. Le contributeur peut créer trois types de ressources: le project, l’issue et le comment.

* ```Project``` : Définit les projets d’une application cliente. C’est la ressource principale utilisée par le client.

* ```Issue``` : Définit les problèmes d'un projet, ainsi que son statut, sa priorité, son attribution (utilisateur auquel le problème est affecté), sa balise (bug, tâche, amélioration). Un project peut posséder plusieurs issues, mais une issue n’est rattachée qu’à un seul project.

* ```Comment``` : Définit les commentaires d'un problème (issue) particulier. Une issue peut avoir plusieurs comments, mais un comment n’est rattaché qu’à une seule issue.


Une base de donnée ```db.sqlite3``` est incluse au dépôt et contient des données générées aléatoirement tels que :

* un ensemble d'utilisateurs (mot de passe par défaut : password)
* un ensemble de projets et de contributeur
* un ensemble d'issues
* un ensemble de comments

## Configuration de l'environnement virtuel :

Le programme utilise plusieurs librairies externes, et modules de Python, qui sont repertoriés dans le fichier ```requirements.txt```

Pour configuer l'environnement, commencez par ouvrir un terminal à la racine du projet, et suivez les étapes suivantes :

1. Créez un environnement virtuel à partir de la commande suivante :
```bash
python -m venv env
```

2. Activez l'environnement virtuel que vous venez de créer avec la commande suivante :

```bash
env/Scripts/activate
```

3. Installez les packages python spécifiés dans le fichier ```requirement.txt``` :

```bash
pip install -r requirement.txt
```
## Lancement du serveur

1. Activez l'environnement virtuel en vous référant à la section précédante.

2. Ouvrez un terminal à la racine du projet, et entrez la commande suivante :

```bash
python ./manage.py runserver
```

## Authentification

L'authentification à l'API se fait au travers de [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).

L'obtention d'un access token se fait avec la requete suivante :

```
POST http://127.0.0.1:8000/api/token/
{
    "username": "username",
    "password": "password"
}
```
Response:
```
{
    "refresh": "eyJhbGc...",
    "access": "eyJhbGci..."
}
```

Le token reçu devra être passé dans les en-tête des requetes.

## Lancement des tests

l'ensemble des tests disponible peuvent être lancés en suivant les étapes suivantes :

1. Activez l'environnement virtuel en vous référant à la section précédante.

2. Ouvrez un terminal à la racine du projet, et entrez la commande suivante :

```bash
python ./manage.py test
```

## Generation de données aleatoires

```
python -W ignore ./manage.py runscript dummy_data
```