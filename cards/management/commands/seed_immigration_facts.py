"""
Seed comprehensive immigration facts
"""
from django.core.management.base import BaseCommand
from cards.models import PolicyFact
from datetime import date


class Command(BaseCommand):
    help = 'Seed immigration facts'

    def handle(self, *args, **kwargs):
        facts = [
            {
                'topic': 'immigration',
                'fact_text': '11 million undocumented immigrants currently reside in the United States (2022 estimate)',
                'source_name': 'Migration Policy Institute',
                'source_url': 'https://www.migrationpolicy.org/data/unauthorized-immigrant-population',
                'date_published': date(2023, 1, 1),
                'fact_type': 'statistic',
                'relevance_score': 95,
            },
            {
                'topic': 'immigration',
                'fact_text': '2.4 million border encounters occurred in fiscal year 2023, the highest on record',
                'source_name': 'US Customs and Border Protection',
                'source_url': 'https://www.cbp.gov/newsroom/stats/southwest-land-border-encounters',
                'date_published': date(2023, 10, 1),
                'fact_type': 'statistic',
                'relevance_score': 90,
            },
            {
                'topic': 'immigration',
                'fact_text': '45% of Fortune 500 companies were founded by immigrants or children of immigrants',
                'source_name': 'New American Economy',
                'source_url': 'https://www.newamericaneconomy.org/issues/entrepreneurship/',
                'date_published': date(2022, 6, 15),
                'fact_type': 'statistic',
                'relevance_score': 85,
            },
            {
                'topic': 'immigration',
                'fact_text': 'Immigrants contribute $458 billion in federal, state, and local taxes annually',
                'source_name': 'New American Economy',
                'source_url': 'https://www.newamericaneconomy.org/issues/tax-contributions/',
                'date_published': date(2022, 3, 1),
                'fact_type': 'statistic',
                'relevance_score': 88,
            },
            {
                'topic': 'immigration',
                'fact_text': '76% of economists surveyed agreed that immigration has a positive economic impact',
                'source_name': 'IGM Chicago Economic Experts Panel',
                'source_url': 'https://www.igmchicago.org/surveys/low-skilled-immigrants/',
                'date_published': date(2021, 9, 1),
                'fact_type': 'poll',
                'relevance_score': 82,
            },
            {
                'topic': 'immigration',
                'fact_text': '29% of US physicians are immigrants, filling critical healthcare workforce gaps',
                'source_name': 'American Immigration Council',
                'source_url': 'https://www.americanimmigrationcouncil.org/research/foreign-trained-doctors-united-states',
                'date_published': date(2022, 7, 1),
                'fact_type': 'statistic',
                'relevance_score': 80,
            },
            {
                'topic': 'immigration',
                'fact_text': 'Immigrants start businesses at twice the rate of native-born Americans',
                'source_name': 'Kauffman Foundation',
                'source_url': 'https://www.kauffman.org/entrepreneurship/reports/immigrant-entrepreneurs/',
                'date_published': date(2022, 5, 1),
                'fact_type': 'study',
                'relevance_score': 83,
            },
            {
                'topic': 'immigration',
                'fact_text': 'Immigration enforcement costs the federal government approximately $18 billion annually',
                'source_name': 'American Immigration Council',
                'source_url': 'https://www.americanimmigrationcouncil.org/research/the-cost-of-immigration-enforcement-and-border-security',
                'date_published': date(2022, 8, 1),
                'fact_type': 'statistic',
                'relevance_score': 78,
            },
            {
                'topic': 'immigration',
                'fact_text': 'The US admits approximately 1 million legal immigrants per year through various programs',
                'source_name': 'Department of Homeland Security',
                'source_url': 'https://www.dhs.gov/immigration-statistics',
                'date_published': date(2023, 1, 1),
                'fact_type': 'statistic',
                'relevance_score': 85,
            },
            {
                'topic': 'immigration',
                'fact_text': '50-70% of agricultural workers in the US are immigrants, many undocumented',
                'source_name': 'National Agricultural Workers Survey',
                'source_url': 'https://www.dol.gov/agencies/eta/national-agricultural-workers-survey',
                'date_published': date(2022, 4, 1),
                'fact_type': 'study',
                'relevance_score': 81,
            },
        ]
        
        for fact_data in facts:
            PolicyFact.objects.update_or_create(
                topic=fact_data['topic'],
                fact_text=fact_data['fact_text'],
                defaults={
                    'source_name': fact_data['source_name'],
                    'source_url': fact_data['source_url'],
                    'date_published': fact_data.get('date_published'),
                    'fact_type': fact_data['fact_type'],
                    'relevance_score': fact_data['relevance_score'],
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {len(facts)} immigration facts!'))
