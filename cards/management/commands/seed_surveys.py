from django.core.management.base import BaseCommand
from cards.models import TopicSurvey, SurveyQuestion, QuestionOption, PolicyFact, Card


class Command(BaseCommand):
    help = 'Seed topic surveys with questions and context from fact database'

    def handle(self, *args, **kwargs):
        # Immigration Survey
        survey, _ = TopicSurvey.objects.get_or_create(
            topic='immigration',
            defaults={
                'title': 'Immigration Policy Survey',
                'description': 'Share your perspective on US immigration policy. Your responses will help generate a personalized argument card.'
            }
        )
        
        # Clear existing questions
        survey.questions.all().delete()
        
        # Get top facts for this topic
        top_facts = PolicyFact.objects.filter(
            topic='immigration'
        ).order_by('-relevance_score')[:10]
        
        # Helper to get stats string
        def get_context_stats(start=0, count=4):
            facts = list(top_facts[start:start+count])
            return '\n'.join([f"• {fact.fact_text}" for fact in facts])
        
        def get_sources(start=0, count=4):
            facts = list(top_facts[start:start+count])
            return ','.join([fact.source_url for fact in facts if fact.source_url])
        
        # Question 1: Overall Stance
        q1 = SurveyQuestion.objects.create(
            survey=survey, 
            order=1, 
            maps_to='stance',
            question_text='What is your overall stance on increasing legal immigration pathways?',
            context_stats=get_context_stats(0, 4),
            learn_more='The US immigration system hasn\'t been comprehensively reformed since 1986. Current debates focus on: expanding legal pathways vs. strengthening enforcement, family reunification vs. merit-based systems, and balancing economic needs with security concerns.',
            sources=get_sources(0, 3)
        )
        QuestionOption.objects.create(question=q1, order=1, option_text='✅ Strongly Support - Expand pathways significantly', card_value='for')
        QuestionOption.objects.create(question=q1, order=2, option_text='👍 Somewhat Support - Moderate expansion', card_value='for')
        QuestionOption.objects.create(question=q1, order=3, option_text='👎 Somewhat Oppose - Maintain current levels', card_value='against')
        QuestionOption.objects.create(question=q1, order=4, option_text='❌ Strongly Oppose - Reduce immigration', card_value='against')
        
        # Question 2: Hypothesis
        q2 = SurveyQuestion.objects.create(
            survey=survey, 
            order=2, 
            maps_to='hypothesis',
            question_text='What is the PRIMARY reason for your position? (Select all that apply)',
            context_stats=get_context_stats(2, 4),
            learn_more='Economic studies show immigration has complex effects. Overall GDP grows, but impacts vary by sector and skill level. High-skilled immigration clearly benefits the economy, while low-skilled immigration\'s effects on wages are debated.',
            sources=get_sources(2, 3)
        )
        QuestionOption.objects.create(question=q2, order=1, option_text='💼 Economic growth - fills labor gaps', 
            card_value='Immigration drives economic growth by filling critical labor shortages and contributing significantly to GDP.')
        QuestionOption.objects.create(question=q2, order=2, option_text='🗽 Humanitarian duty - nation of immigrants', 
            card_value='The United States has a moral obligation to provide refuge and opportunity.')
        QuestionOption.objects.create(question=q2, order=3, option_text='🛡️ National security - need border control', 
            card_value='Current immigration levels strain our ability to properly vet newcomers and secure borders.')
        QuestionOption.objects.create(question=q2, order=4, option_text='💰 Worker protection - protect wages', 
            card_value='Increased immigration can depress wages and displace American workers.')
        
        # Continue with questions 3-10...
        # (Using simplified versions for now)
        
        for i in range(3, 11):
            q = SurveyQuestion.objects.create(
                survey=survey,
                order=i,
                maps_to='supporting' if i <= 5 else ('opposing' if i <= 8 else ('scope' if i == 9 else 'conclusion')),
                question_text=f'Question {i} placeholder',
                context_stats=get_context_stats(i-1, 3),
                sources=get_sources(i-1, 2)
            )
            
            for j in range(1, 5):
                QuestionOption.objects.create(
                    question=q,
                    order=j,
                    option_text=f'Option {j}',
                    card_value=f'Card value for Q{i} Option{j}'
                )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Immigration survey seeded with {survey.questions.count()} questions!'))
