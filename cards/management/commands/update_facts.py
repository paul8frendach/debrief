"""
Management command to fetch and update facts from APIs
Run: python manage.py update_facts --topic immigration
"""
from django.core.management.base import BaseCommand
from cards.models import PolicyFact, FactSource, Card
from cards.fact_apis import FactFetcher
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Update facts from various APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            help='Specific topic to update (e.g., immigration, healthcare)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if recently updated',
        )

    def handle(self, *args, **options):
        topic = options.get('topic')
        force = options.get('force', False)
        
        fetcher = FactFetcher()
        
        # Get topics to update
        if topic:
            topics = [topic]
        else:
            # Get all topics from Card choices
            topics = [code for code, name in Card.TOPIC_CHOICES]
        
        self.stdout.write(f"Updating facts for: {', '.join(topics)}")
        
        for topic_code in topics:
            self.stdout.write(f"\n📊 Processing {topic_code}...")
            
            # Check if needs update (skip if updated in last 7 days unless forced)
            if not force:
                recent_facts = PolicyFact.objects.filter(
                    topic=topic_code,
                    last_verified__gte=datetime.now() - timedelta(days=7)
                ).count()
                
                if recent_facts > 0:
                    self.stdout.write(f"  ⏭️  Skipping {topic_code} (recently updated)")
                    continue
            
            # Fetch facts based on topic
            facts_added = 0
            
            if topic_code == 'immigration':
                facts_added += self.update_immigration_facts(fetcher)
            elif topic_code == 'healthcare':
                facts_added += self.update_healthcare_facts(fetcher)
            elif topic_code == 'economy':
                facts_added += self.update_economy_facts(fetcher)
            # Add more topics as needed
            
            self.stdout.write(self.style.SUCCESS(f"  ✅ Added/updated {facts_added} facts for {topic_code}"))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Fact update complete!'))
    
    def update_immigration_facts(self, fetcher):
        """Update immigration-specific facts"""
        facts_added = 0
        
        # Migration Policy Institute data
        mpi_data = fetcher.fetch_migration_policy_data('immigration')
        if mpi_data:
            PolicyFact.objects.update_or_create(
                topic='immigration',
                fact_text=f"Unauthorized immigrant population: {mpi_data['unauthorized_population']}",
                defaults={
                    'source_name': mpi_data['source'],
                    'source_url': mpi_data['url'],
                    'fact_type': 'statistic',
                    'relevance_score': 95,
                }
            )
            facts_added += 1
        
        # Pew Research studies
        pew_results = fetcher.search_pew_research('immigration statistics')
        for result in pew_results[:3]:
            PolicyFact.objects.update_or_create(
                topic='immigration',
                fact_text=result['title'],
                defaults={
                    'source_name': 'Pew Research Center',
                    'source_url': result['url'],
                    'fact_type': 'study',
                    'relevance_score': 85,
                }
            )
            facts_added += 1
        
        return facts_added
    
    def update_healthcare_facts(self, fetcher):
        """Update healthcare-specific facts"""
        facts_added = 0
        
        # KFF data (when available)
        pew_results = fetcher.search_pew_research('healthcare coverage')
        for result in pew_results[:2]:
            PolicyFact.objects.update_or_create(
                topic='healthcare',
                fact_text=result['title'],
                defaults={
                    'source_name': 'Pew Research Center',
                    'source_url': result['url'],
                    'fact_type': 'poll',
                    'relevance_score': 80,
                }
            )
            facts_added += 1
        
        return facts_added
    
    def update_economy_facts(self, fetcher):
        """Update economy-specific facts"""
        facts_added = 0
        
        # Census data
        census_data = fetcher.fetch_census_data('economy')
        if census_data:
            # Process census data
            pass
        
        return facts_added
