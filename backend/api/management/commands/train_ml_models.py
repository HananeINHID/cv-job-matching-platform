import os
import pickle
import logging
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from api.models import JobOffer

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Retrain the ML models (KMeans and TF-IDF) using current database data."

    def handle(self, *args, **options):
        self.stdout.write("Fetching job offers from database...")
        offres = JobOffer.objects.filter(is_active=True)
        
        if offres.count() < 5:
            self.stdout.write(self.style.ERROR("Not enough data to train (at least 5 active offers required)."))
            return

        texts = [
            " ".join(filter(None, [o.title, o.required_skills, o.description]))
            for o in offres
        ]

        self.stdout.write(f"Training TF-IDF Vectorizer on {len(texts)} documents...")
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        X = vectorizer.fit_transform(texts)

        n_clusters = min(5, len(texts))
        self.stdout.write(f"Training KMeans with {n_clusters} clusters...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(X)

        # Define paths
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        ML_MODELS_DIR = os.path.join(BASE_DIR, 'ml_models')
        os.makedirs(ML_MODELS_DIR, exist_ok=True)

        kmeans_path = os.path.join(ML_MODELS_DIR, 'kmeans_model.pkl')
        vectorizer_path = os.path.join(ML_MODELS_DIR, 'vectorizer_tfidf.pkl')

        self.stdout.write(f"Saving models to {ML_MODELS_DIR}...")
        with open(kmeans_path, 'wb') as f:
            pickle.dump(kmeans, f)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)

        self.stdout.write(self.style.SUCCESS("ML models successfully retrained and saved."))
