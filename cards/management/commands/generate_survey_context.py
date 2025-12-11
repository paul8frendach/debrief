"""
Generate contextual information for survey questions using AI and fact database
Run: python manage.py generate_survey_context --topic immigration
"""
from django.core.management.base import BaseCommand
from cards.models import TopicSurvey, SurveyQuestion, PolicyFact
from cards.fact_apis import AIFactGenerator
import json


class Command(BaseCommand):
    help = 'Generate or update context for survey questions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            required=True,
            help='Topic code (e.g., immigration)',
        )
        parser.add_argument(
            '--use-ai',
            action='store_true',
            help='Use AI to generate context (requires ANTHROPIC_API_KEY)',
        )

    def handle(self, *args, **options):
        topic = options['topic']
        use_ai = options.get('use_ai', False)
        
        try:
            survey = TopicSurvey.objects.get(topic=topic)
        except TopicSurvey.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Survey for topic "{topic}" not found'))
            return
        
        self.stdout.write(f"Generating context for {survey.title}...")
        
        questions = survey.questions.all()
        
        for question in questions:
            self.stdout.write(f"\n📝 Question {question.order}: {question.question_text[:50]}...")
            
            # Get relevant facts from database
            relevant_facts = PolicyFact.objects.filter(
                topic=topic
            ).order_by('-relevance_score')[:5]
            
            # Build context_stats from facts
            stats_list = []
            sources_list = []
            
            for fact in relevant_facts[:4]:
                stats_list.append(f"• {fact.fact_text}")
                if fact.source_url:
                    sources_list.append(fact.source_url)
            
            if stats_list:
                question.context_stats = '\n'.join(stats_list)
                question.sources = ','.join(sources_list)
            
            # Use AI to generate learn_more if requested
            if use_ai and not question.learn_more:
                ai_gen = AIFactGenerator()
                ai_context = ai_gen.generate_question_context(topic, question.question_text)
                
                if ai_context:
                    try:
                        # Parse AI response
                        context_data = json.loads(ai_context)
                        question.learn_more = context_data.get('learn_more', '')
                        self.stdout.write("  ✅ Generated AI context")
                    except json.JSONDecodeError:
                        # If not JSON, use as-is
                        question.learn_more = ai_context
                        self.stdout.write("  ✅ Added AI context (raw)")
            
            question.save()
            self.stdout.write(self.style.SUCCESS(f"  ✅ Updated question {question.order}"))
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Context generation complete for {survey.title}!'))
