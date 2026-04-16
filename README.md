# EBMS OBR Mock Server

Mock fidèle de l'API eBMS de l'OBR (v0.5) pour tests d'intégration.

## Endpoints disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/ebms_api/login/` | Authentification → JWT (60s) |
| POST | `/ebms_api/addInvoice_confirm/` | Ajout facture avec accusé de réception |
| POST | `/ebms_api/getInvoice/` | Récupération facture |
| POST | `/ebms_api/cancelInvoice/` | Annulation facture |
| POST | `/ebms_api/checkTIN/` | Vérification NIF |
| POST | `/ebms_api/AddStockMovement/` | Mouvement de stock |
| GET  | `/ebms_api/public_key/` | Clé publique RSA pour vérifier signatures |

## Lancer en local

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

## Déployer sur Render

1. Push ce dossier sur GitHub
2. Créer un nouveau Web Service sur render.com
3. Pointer sur le repo → Render détecte `render.yaml` automatiquement
4. Configurer les variables d'env (`JWT_SECRET`, `EBMS_USERNAME`, `EBMS_PASSWORD`)

## Déployer sur Railway

```bash
railway login
railway init
railway up
```
Variables à ajouter dans Railway Dashboard :
- `JWT_SECRET`
- `EBMS_USERNAME`
- `EBMS_PASSWORD`

## Notes

- **checkTIN** : considère valide tout NIF de 10 chiffres
- **Token JWT** expire après 60 secondes (identique à l'OBR)
- **Signature électronique** : RSA 2048 + SHA-256, régénérée à chaque redémarrage
- La clé publique est accessible via `GET /ebms_api/public_key/`
