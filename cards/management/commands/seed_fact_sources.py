from django.core.management.base import BaseCommand
from cards.models import FactSource


class Command(BaseCommand):
    help = 'Seed trusted fact sources'

    def handle(self, *args, **kwargs):
        sources = [
            {
                'name': 'US Census Bureau',
                'base_url': 'https://www.census.gov/',
                'api_endpoint': 'https://api.census.gov/data',
                'api_key_required': False,
                'credibility_rating': 95,
                'source_type': 'government',
                'topics': ['immigration', 'economy', 'demographics', 'housing'],
            },
            {
                'name': 'Pew Research Center',
                'base_url': 'https://www.pewresearch.org/',
                'api_endpoint': '',
                'api_key_required': False,
                'credibility_rating': 90,
                'source_type': 'think_tank',
                'topics': ['immigration', 'politics', 'social_issues', 'demographics'],
            },
            {
                'name': 'Migration Policy Institute',
                'base_url': 'https://www.migrationpolicy.org/',
                'api_endpoint': '',
                'api_key_required': False,
                'credibility_rating': 95,
                'source_type': 'think_tank',
                'topics': ['immigration'],
            },
            {
                'name': 'Congressional Budget Office',
                'base_url': 'https://www.cbo.gov/',
                'api_endpoint': '',
                'api_key_required': False,
                'credibility_rating': 95,
                'source_type': 'government',
                'topics': ['economy', 'healthcare', 'tax_policy', 'budget'],
            },
            {
                'name': 'Bureau of Labor Statistics',
                'base_url': 'https://www.bls.gov/',
                'api_endpoint': 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
                'api_key_required': False,
                'credibility_rating': 95,
                'source_type': 'government',
                'topics': ['economy', 'employment', 'wages'],
            },
            {
                'name': 'FactCheck.org',
                'base_url': 'https://www.factcheck.org/',
                'api_endpoint': '',
                'api_key_required': False,
                'credibility_rating': 85,
                'source_type': 'ngo',
                'topics': ['politics', 'all'],
            },
            {
                'name': 'Kaiser Family Foundation',
                'base_url': 'https://www.kff.org/',
                'api_endpoint': '',
                'api_key_required': False,
                'credibility_rating': 90,
                'source_type': 'think_tank',
                'topics': ['healthcare'],
            },
        ]
        
        for source_data in sources:
            FactSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(sources)} fact sources!'))
