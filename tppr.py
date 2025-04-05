import requests
from flask import Flask, redirect, request, session, url_for, render_template_string, send_file
from urllib.parse import urlencode
import io
import zipfile
import re

def safe_filename(name):
    """Génère un nom de fichier sécurisé en remplaçant les caractères non alphanumériques."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)

app = Flask(__name__)
app.secret_key = "UNE_CLE_SECRETE_A_MODIFIER"  # Veuillez changer cette valeur pour sécuriser vos sessions

# Entête stylisée à afficher sur chaque page
STYLED_HEADER = """
<div style="background-color: #2e3b4e; padding: 20px; color: white; text-align: center; margin-bottom: 20px;">
  <h1 style="margin: 0;">Twitch Profile Picture Retriever (TPPR)</h1>
  <p style="margin: 0;">by S0URC3K0D</p>
</div>
"""

# Remplacez ces valeurs par vos identifiants Twitch
CLIENT_ID = "VOTRE_CLIENT_ID"
CLIENT_SECRET = "VOTRE_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:5000/twitch_callback"
# Scope nécessaire pour récupérer les infos utilisateur et la liste des abonnés
SCOPE = "user:read:email channel:read:subscriptions"

@app.route("/")
def index():
    if "access_token" in session:
        return STYLED_HEADER + """
        <h2>Bienvenue, {} !</h2>
        <p><a href="/subscribers">Voir les abonnés de la chaîne</a></p>
        <p><a href="/download_images">Télécharger les photos de profil des abonnés</a></p>
        <p><a href="/logout">Se déconnecter</a></p>
        """.format(session.get("display_name", "Utilisateur"))
    else:
        return STYLED_HEADER + """
        <h2>Bienvenue dans l'application Twitch !</h2>
        <p><a href="/login">Se connecter avec Twitch</a></p>
        """

@app.route("/login")
def login():
    base_auth_url = "https://id.twitch.tv/oauth2/authorize"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",  # Utilisation du flux Authorization Code
        "scope": SCOPE,
        "force_verify": "true"   # Optionnel, pour forcer l'authentification
    }
    auth_url = f"{base_auth_url}?{urlencode(params)}"
    return redirect(auth_url)

@app.route("/twitch_callback")
def twitch_callback():
    code = request.args.get("code")
    if not code:
        return "Erreur : aucun code reçu.", 400

    # Échange du code contre un access token
    token_url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    token_response = requests.post(token_url, data=data)
    if not token_response.ok:
        return f"Erreur lors de l'échange du code contre un token : {token_response.status_code}", token_response.status_code

    tokens = token_response.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return "Erreur : access token non reçu.", 400

    session["access_token"] = access_token

    # Récupération des informations de l'utilisateur (le diffuseur)
    headers = {
        "Client-Id": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    user_response = requests.get("https://api.twitch.tv/helix/users", headers=headers)
    if not user_response.ok:
        return f"Erreur lors de la récupération des informations utilisateur: {user_response.status_code}", user_response.status_code

    user_data = user_response.json().get("data")
    if not user_data or len(user_data) == 0:
        return "Aucun utilisateur trouvé.", 404

    user_info = user_data[0]
    session["broadcaster_id"] = user_info.get("id")
    session["display_name"] = user_info.get("display_name")

    return redirect(url_for("index"))

@app.route("/subscribers")
def subscribers():
    if "access_token" not in session or "broadcaster_id" not in session:
        return redirect(url_for("index"))
        
    access_token = session["access_token"]
    broadcaster_id = session["broadcaster_id"]
    
    headers = {
        "Client-Id": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    
    # Récupération des abonnés via l'endpoint Get Broadcaster Subscriptions
    subs_url = "https://api.twitch.tv/helix/subscriptions"
    params = {"broadcaster_id": broadcaster_id, "first": 100}  # Jusqu'à 100 abonnés
    subs_response = requests.get(subs_url, headers=headers, params=params)
    if not subs_response.ok:
        return f"Erreur lors de la récupération des abonnés: {subs_response.status_code}", subs_response.status_code

    subs_data = subs_response.json().get("data", [])
    if not subs_data:
        return STYLED_HEADER + "<p>Aucun abonnement trouvé ou vous ne disposez pas des permissions requises.</p>"

    # Extraction des user_id des abonnés
    user_ids = [sub.get("user_id") for sub in subs_data if sub.get("user_id")]
    
    # Récupération des informations des abonnés via l'endpoint Get Users
    users_url = "https://api.twitch.tv/helix/users"
    users_params = [("id", uid) for uid in user_ids]
    users_response = requests.get(users_url, headers=headers, params=users_params)
    if not users_response.ok:
        return f"Erreur lors de la récupération des informations des abonnés: {users_response.status_code}", users_response.status_code

    users_data = users_response.json().get("data", [])
    
    html_content = STYLED_HEADER + "<h1 style='text-align:center;'>Abonnés de la chaîne</h1>"
    html_content += "<ul style='list-style: none;padding: 0;'>"
    for user in users_data:
        display_name = user.get("display_name", "Inconnu")
        profile_image_url = user.get("profile_image_url")
        html_content += f"""
        <li style="margin-bottom: 10px; text-align:center;">
            <img src="{profile_image_url}" alt="Photo profil de {display_name}" 
                 style="width:50px;height:50px;border-radius:50%;vertical-align:middle;margin-right:10px;">
            <span>{display_name}</span>
        </li>
        """
    html_content += "</ul>"
    html_content += '<p style="text-align:center;"><a href="/download_images">Télécharger les photos de profil</a></p>'
    
    return render_template_string(html_content)

@app.route("/download_images")
def download_images():
    if "access_token" not in session or "broadcaster_id" not in session:
        return redirect(url_for("index"))
        
    access_token = session["access_token"]
    broadcaster_id = session["broadcaster_id"]
    
    headers = {
        "Client-Id": CLIENT_ID,
        "Authorization": f"Bearer {access_token}"
    }
    
    # Récupération des abonnés via l'endpoint Get Broadcaster Subscriptions
    subs_url = "https://api.twitch.tv/helix/subscriptions"
    params = {"broadcaster_id": broadcaster_id, "first": 100}
    subs_response = requests.get(subs_url, headers=headers, params=params)
    if not subs_response.ok:
        return f"Erreur lors de la récupération des abonnés: {subs_response.status_code}", subs_response.status_code

    subs_data = subs_response.json().get("data", [])
    if not subs_data:
        return STYLED_HEADER + "<p>Aucun abonnement trouvé ou permissions insuffisantes.</p>"
    
    # Extraction des user_id
    user_ids = [sub.get("user_id") for sub in subs_data if sub.get("user_id")]
    
    # Récupération des infos utilisateur afin d'obtenir les photos de profil
    users_url = "https://api.twitch.tv/helix/users"
    users_params = [("id", uid) for uid in user_ids]
    users_response = requests.get(users_url, headers=headers, params=users_params)
    if not users_response.ok:
        return f"Erreur lors de la récupération des informations des abonnés: {users_response.status_code}", users_response.status_code

    users_data = users_response.json().get("data", [])
    
    # Création d'une archive ZIP en mémoire contenant les images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for user in users_data:
            display_name = user.get("display_name", "inconnu")
            profile_image_url = user.get("profile_image_url")
            if profile_image_url:
                img_response = requests.get(profile_image_url)
                if img_response.ok:
                    content_type = img_response.headers.get("Content-Type", "").lower()
                    if "jpeg" in content_type:
                        ext = "jpg"
                    elif "png" in content_type:
                        ext = "png"
                    else:
                        ext = "jpg"
                    filename = f"{safe_filename(display_name)}.{ext}"
                    zip_file.writestr(filename, img_response.content)
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="profile_images.zip"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
