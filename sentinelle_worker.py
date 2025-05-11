
# sentinelle_worker.py – Agent GPT exécuteur de sentinelle.json
import os
import json
import time
from datetime import datetime
import openai
from fpdf import FPDF
import unicodedata

# === CONFIGURATION ===
BASE_PATH = "/data/Hub_Personnel"
COMMAND_PATH = os.path.join(BASE_PATH, "GlitchOps/Sentinelle/sentinelle.json")
LOG_PATH = os.path.join(BASE_PATH, "GlitchOps/Sentinelle/logs")
openai.api_key = os.environ.get("OPENAI_API_KEY")

# === UTILS ===
def log_event(msg):
    os.makedirs(LOG_PATH, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(LOG_PATH, f"log_{stamp}.txt"), "w") as f:
        f.write(f"[Sentinelle] {msg}\n")
    print(f"[Sentinelle] {msg}")

def clean(text):
    return unicodedata.normalize("NFKD", text).encode("latin-1", "ignore").decode("latin-1")

def generate_summary(params):
    prompt = "Résumé demandé: " + json.dumps(params)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es une IA de synthèse."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def generate_pdf(cible, prompt, titre):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    contenu = response["choices"][0]["message"]["content"].strip()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titre, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    for ligne in contenu.split("\n"):
        pdf.multi_cell(0, 8, clean(ligne))
    dossier = os.path.join(BASE_PATH, cible, "pdf_routines")
    os.makedirs(dossier, exist_ok=True)
    nom_fichier = f"{titre.replace(' ', '_')}_{datetime.now().date()}.pdf"
    chemin_fichier = os.path.join(dossier, nom_fichier)
    pdf.output(chemin_fichier)
    return chemin_fichier

# === BOUCLE PRINCIPALE ===
def sentinelle_loop():
    log_event("Agent actif. Surveillance du JSON en cours...")
    while True:
        if os.path.exists(COMMAND_PATH):
            try:
                with open(COMMAND_PATH, "r") as f:
                    commande = json.load(f)

                if commande.get("status") == "pending":
                    type_cmd = commande.get("type")
                    params = commande.get("params", {})
                    result = ""

                    if type_cmd == "generate_summary":
                        result = generate_summary(params)
                    elif type_cmd == "generate_pdf":
                        prompt = f"Génère une version claire, lisible et structurée de : {params.get('but', '')}"
                        result = generate_pdf(params.get("cible", "Logs"), prompt, params.get("titre", "Rapport"))
                    else:
                        result = f"⚠️ Commande inconnue : {type_cmd}"

                    commande["status"] = "done"
                    commande["executed_at"] = datetime.now().isoformat()
                    commande["result"] = result

                    with open(COMMAND_PATH, "w") as f:
                        json.dump(commande, f, indent=2)

                    log_event(f"Commande '{type_cmd}' exécutée.")

            except Exception as e:
                log_event(f"Erreur de traitement : {str(e)}")

        time.sleep(30)

if __name__ == "__main__":
    sentinelle_loop()
