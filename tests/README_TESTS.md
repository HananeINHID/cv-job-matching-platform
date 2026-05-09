# Guide des Tests Backend & Liaison

Ce dossier contient les tests pour la plateforme **CV Job Matching** (Backend Django 6 + DRF). 
À la demande, cette suite est concentrée uniquement sur les aspects Backend (logique métier, API, ML) et Liaison (Contrats API).

## Architecture des Tests

```text
tests/
├── backend/
│   ├── unit/            # Logique pure sans dépendances (Scoring, NLP, Models, Scraping mocké)
│   ├── integration/     # Tests API complets avec base de données SQLite en mémoire
│   └── conftest.py      # Fixtures globales (client API authentifié, offres d'emploi, etc.)
└── liaison/
    ├── test_api_contracts.py  # Vérifie que les JSON retournés correspondent au front
    └── test_data_flow.py      # Vérifie un scénario d'utilisation (inscription -> matching)
```

## Pré-requis

Les tests nécessitent :
- `pytest`
- `pytest-django`
- `djangorestframework-simplejwt`

## Comment Lancer les Tests

Se placer à la racine du projet `cv-job-matching-platform/` et exécuter `pytest` sur les dossiers souhaités :

### 1. Tous les tests
```bash
pytest tests/
```

### 2. Tests unitaires uniquement (très rapide)
```bash
pytest tests/backend/unit/
```

### 3. Tests d'API (Intégration)
```bash
pytest tests/backend/integration/
```

### 4. Tests de Contrats et Flux (Liaison)
```bash
pytest tests/liaison/
```

## Couverture Attendue
- **Scoring & NLP** : L'algorithme de calcul des similarités (Cosinus, Jaccard, Geo) est couvert à 100%.
- **Modèles Django** : Création et cascade delete.
- **Endpoints DRF** : Codes de statut HTTP, authentification requise, JWT.
- **Scraping** : Parsing basé sur des mocks de HTML pour s'assurer que les extracteurs marchent sans requête réseau.
