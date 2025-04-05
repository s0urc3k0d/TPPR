# Twitch Profile Picture Retriever (TPPR)

**Twitch Profile Picture Retriever (TPPR)** est une application web développée en Python avec Flask. Elle permet aux streamers de leur chaîne Twitch d'afficher et de télécharger les photos de profil de leurs abonnés.

## Description

L'application fonctionne en deux temps :

1. **Authentification OAuth avec Twitch**  
   Le flux OAuth (Authorization Code Grant) est utilisé pour authentifier l'utilisateur et obtenir un **access token**. Cet identifiant permet ensuite d'accéder aux ressources protégées de l'API Twitch, notamment pour récupérer les informations du diffuseur ainsi que la liste de ses abonnés.

2. **Récupération et affichage des photos de profil**  
   Une fois authentifié, l'application :
   - Récupère la liste des abonnés (via l'endpoint *Get Broadcaster Subscriptions*) avec le scope `channel:read:subscriptions` (nécessite un compte ayant les droits requis).
   - Interroge l'endpoint *Get Users* pour obtenir les informations détaillées de chaque abonné, dont leur photo de profil.
   - Affiche ces images avec le pseudo de chaque abonné dans une interface web.
   - Propose de télécharger l'ensemble des photos dans une archive ZIP, où chaque image est renommée avec le pseudo (après nettoyage des caractères non autorisés).

## Fonctionnalités

- **Authentification via Twitch:**  
  Permet d'entrer dans l'écosystème Twitch en utilisant OAuth.  
- **Affichage des abonnés:**  
  Visualisation en temps réel des photos de profil et des pseudos des abonnés de la chaîne.
- **Téléchargement des images:**  
  Regroupement et téléchargement des photos de profil dans une archive ZIP.
- **Entête personnalisée:**  
  Chaque page affiche une entête stylisée avec le nom de l'application et l'auteur **S0URC3K0D**.

## Prérequis

- **Python 3.6** ou version ultérieure.
- **Compte développeur Twitch :**  
  Une application doit être enregistrée sur [Twitch Developer Console](https://dev.twitch.tv/console) avec une URL de redirection (par exemple, `http://localhost:5000/twitch_callback`).
- **Permissions requises :**  
  - `user:read:email`
  - `channel:read:subscriptions` (nécessaire pour récupérer la liste des abonnés – accès réservé aux chaînes disposant de droits spécifiques).
- **Dépendances Python :**  
  Les packages suivants sont nécessaires (voir le fichier `requirements.txt`) :
  ```txt
  Flask==3.1.0
  requests==2.32.3

## Installation

1. **Cloner le dépôt**  
   ```bash
   git clone https://github.com/s0urc3k0d/TPPR.git
   cd TPPR

2. **Installer les dépendances**  
   ```bash
   pip install -r requirements.txt

3. **Configurer l'application**  
   ```bash
   pip install -r requirements.txt

4. **Lancer l'application**  
   ```bash
   python tppr.py

## Utilisation

1. **Accéder à l'application**  
   Ouvrez votre navigateur et rendez-vous sur [http://localhost:5000](http://localhost:5000).

2. **Authentification**  
   Cliquez sur le lien **"Se connecter avec Twitch"** pour lancer le processus d'authentification via OAuth.

3. **Visualiser les abonnés**  
   Une fois authentifié, l'application affiche la liste de vos abonnés avec leurs photos de profil et leurs pseudos.

4. **Télécharger les images**  
   Cliquez sur le lien **"Télécharger les photos de profil"** pour générer et télécharger une archive ZIP contenant les images. Chaque image est renommée selon le pseudo de l'abonné (les noms sont nettoyés pour exclure les caractères spéciaux).

## Licence

Twitch Profile Picture Retriever (TPPR) est un logiciel libre distribué sous la licence GNU General Public License v3.0 (GPLv3).

```text
Copyright (C) [2025]  
S0URC3K0D

Ce programme est libre ; vous pouvez le redistribuer et/ou le modifier selon les termes de la GNU General Public License publiée par la Free Software Foundation, soit la version 3 du GPL, soit (à votre choix) toute version ultérieure.

Ce programme est distribué dans l'espoir qu'il soit utile, mais SANS AUCUNE GARANTIE, ni garantie implicite de COMMERCIALISABILITÉ ou d'ADÉQUATION À UN USAGE PARTICULIER.

Vous devriez avoir reçu une copie de la GNU General Public License avec ce programme. Si ce n'est pas le cas, consultez :  
<https://www.gnu.org/licenses/gpl-3.0.html>
