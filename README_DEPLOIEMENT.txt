1. Crée un dépôt GitHub (ex: sentinelle-automatique)
2. Upload tout le contenu du dossier (pas dans un sous-dossier)
3. Connecte ton compte GitHub à Render.com
4. Crée un Cron Job
   - Schedule: 59 23 * * * (quotidien)
   - Start Command: python sentinelle_runner_daily.py
   - Pour l’hebdo: même étape mais fichier sentinelle_runner_weekly.py
5. Active et vérifie les logs depuis Render
