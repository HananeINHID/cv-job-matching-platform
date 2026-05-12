import time
import random
import sys
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from api.models import JobOffer

# Add project root to sys.path to import scrapers
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scraping.emploi import RekruteScraper, EmploiMaScraper, MarocAnnoncesScraper, LinkedInScraper

KEYWORDS_LIST = [
    "Data Scientist", "Développeur Python", "Développeur Fullstack", 
    "DevOps", "Data Engineer", "Cloud Engineer"
]

class Command(BaseCommand):
    help = "Scrape jobs from multiple sources and save to database."

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, default='all', help='Source: rekrute, emploima, linkedin, marocannonces, all')
        parser.add_argument('--keyword', type=str, help='Specific keyword to search')
        parser.add_argument('--limit', type=int, default=10, help='Max offers per source/keyword')

    def save_offers(self, raw_offers, source_name):
        saved = 0
        for data in raw_offers:
            title = (data.get('title') or 'N/A')[:255]
            company = (data.get('company') or 'N/A')[:255]

            if JobOffer.objects.filter(title=title, company=company).exists():
                continue

            raw_source = data.get('source') or ''
            source_url = raw_source.split('|', 1)[1].strip() if '|' in raw_source else ''

            posted_date = None
            raw_date = data.get('posted_date')
            if raw_date:
                try:
                    posted_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
                except ValueError:
                    pass

            try:
                JobOffer.objects.create(
                    title=title,
                    company=company,
                    location=(data.get('location') or 'Maroc')[:255],
                    sector=(data.get('sector') or '')[:255],
                    description=data.get('description') or '',
                    required_skills=data.get('required_skills') or '',
                    required_education=data.get('required_education') or '',
                    required_experience=(data.get('required_experience') or '')[:100],
                    required_languages=data.get('required_languages') or '',
                    contract_type=(data.get('contract_type') or '')[:100],
                    posted_date=posted_date,
                    source=source_name,
                    source_url=source_url,
                    is_active=True
                )
                saved += 1
                self.stdout.write(f"  [OK] Saved: {title}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  [ERROR] Could not save {title}: {e}"))
        return saved

    def handle(self, *args, **options):
        # Fix encoding for Windows console
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

        source_arg = options['source'].lower()
        keyword_arg = options['keyword']
        limit = options['limit']

        keywords = [keyword_arg] if keyword_arg else KEYWORDS_LIST
        sources = ['rekrute', 'emploima', 'marocannonces', 'linkedin'] if source_arg == 'all' else [source_arg]

        for source in sources:
            self.stdout.write(self.style.SUCCESS(f"\n--- Starting Scraper: {source.upper()} ---"))
            
            for kw in keywords:
                self.stdout.write(f"Searching for '{kw}'...")
                progress = {source: {kw: 1}}
                raw_data = []

                try:
                    if source == 'rekrute':
                        scraper = RekruteScraper()
                        raw_data = scraper.scrape(kw, progress, pages=max(1, limit // 10))
                    elif source == 'marocannonces':
                        scraper = MarocAnnoncesScraper()
                        raw_data = scraper.scrape(kw, progress, pages=max(1, limit // 10))
                    elif source == 'emploima':
                        scraper = EmploiMaScraper()
                        try:
                            raw_data = scraper.scrape(kw, progress, max_offers=limit)
                        finally:
                            scraper.quit()
                    elif source == 'linkedin':
                        scraper = LinkedInScraper()
                        try:
                            raw_data = scraper.scrape(kw, progress, max_offers=limit)
                        finally:
                            scraper.quit()
                    
                    new_saved = self.save_offers(raw_data, source)
                    self.stdout.write(self.style.SUCCESS(f"Finished '{kw}': {new_saved} new offers saved."))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Critical error for {source}/{kw}: {e}"))

        self.stdout.write(self.style.SUCCESS("\nAll scraping tasks completed."))
