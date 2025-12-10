from django.core.management.base import BaseCommand
from cards.models import TopicSurvey, SurveyQuestion, QuestionOption, Card


class Command(BaseCommand):
    help = 'Seed topic surveys with questions'

    def handle(self, *args, **kwargs):
        # Immigration Survey
        survey, _ = TopicSurvey.objects.get_or_create(
            topic='immigration',
            defaults={
                'title': 'Immigration Policy Survey',
                'description': '📊 Context: The US has approximately 11 million undocumented immigrants. Border encounters reached 2.4 million in 2023. The debate centers on border security, pathways to citizenship, and economic impact.'
            }
        )
        
        # Clear existing questions
        survey.questions.all().delete()
        
        # Question 1: Overall Stance
        q1 = SurveyQuestion.objects.create(
            survey=survey, order=1, maps_to='stance',
            question_text='What is your overall stance on increasing legal immigration pathways?'
        )
        QuestionOption.objects.create(question=q1, order=1, option_text='✅ Strongly Support - Expand pathways significantly', card_value='for')
        QuestionOption.objects.create(question=q1, order=2, option_text='👍 Somewhat Support - Moderate expansion', card_value='for')
        QuestionOption.objects.create(question=q1, order=3, option_text='👎 Somewhat Oppose - Maintain current levels', card_value='against')
        QuestionOption.objects.create(question=q1, order=4, option_text='❌ Strongly Oppose - Reduce immigration', card_value='against')
        
        # Question 2: Hypothesis/Core Belief
        q2 = SurveyQuestion.objects.create(
            survey=survey, order=2, maps_to='hypothesis',
            question_text='What is the PRIMARY reason for your position? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q2, order=1, option_text='💼 Economic growth - Immigrants fill labor gaps and create jobs', 
            card_value='Immigration drives economic growth by filling critical labor shortages, starting businesses at higher rates, and contributing $2 trillion to GDP annually.')
        QuestionOption.objects.create(question=q2, order=2, option_text='🗽 Humanitarian duty - America is a nation of immigrants', 
            card_value='The United States has a moral obligation to provide refuge and opportunity, consistent with our values as a nation of immigrants.')
        QuestionOption.objects.create(question=q2, order=3, option_text='🛡️ National security - Need stronger border control', 
            card_value='Current immigration levels strain our ability to properly vet newcomers and secure borders, prioritizing security is essential.')
        QuestionOption.objects.create(question=q2, order=4, option_text='💰 Worker protection - Protect American wages and jobs', 
            card_value='Increased immigration can depress wages and displace American workers, particularly in lower-skilled sectors.')
        
        # Question 3: Economic Benefits (Supporting)
        q3 = SurveyQuestion.objects.create(
            survey=survey, order=3, maps_to='supporting',
            question_text='Which economic benefits do you see? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q3, order=1, option_text='📈 Innovation - 45% of Fortune 500 companies founded by immigrants', 
            card_value='Immigrants drive innovation and entrepreneurship, with 45% of Fortune 500 companies founded by immigrants or their children')
        QuestionOption.objects.create(question=q3, order=2, option_text='🏥 Workforce gaps - Fill critical healthcare and agriculture jobs', 
            card_value='29% of physicians and 38% of home health aides are immigrants, filling essential workforce shortages')
        QuestionOption.objects.create(question=q3, order=3, option_text='💵 Tax revenue - Immigrants contribute billions in taxes', 
            card_value='Immigrants contribute $458 billion in federal, state, and local taxes annually')
        QuestionOption.objects.create(question=q3, order=4, option_text='📊 Population growth - Offset declining birth rates', 
            card_value='Immigration helps maintain population growth needed to support Social Security and economic expansion')
        
        # Question 4: Border Security (Supporting)
        q4 = SurveyQuestion.objects.create(
            survey=survey, order=4, maps_to='supporting',
            question_text='How should border security be addressed? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q4, order=1, option_text='🎯 Legal pathways reduce illegal crossings', 
            card_value='Creating accessible legal pathways reduces incentives for dangerous illegal border crossings')
        QuestionOption.objects.create(question=q4, order=2, option_text='🔍 Better vetting through legal process', 
            card_value='Streamlined legal processes enable better tracking, vetting, and integration of immigrants')
        QuestionOption.objects.create(question=q4, order=3, option_text='⚡ Technology over walls - Smart border security', 
            card_value='Modern surveillance technology and personnel are more effective than physical barriers')
        QuestionOption.objects.create(question=q4, order=4, option_text='🤝 Regional cooperation - Work with origin countries', 
            card_value='Partnering with Central American countries to address root causes of migration')
        
        # Question 5: Integration (Supporting)
        q5 = SurveyQuestion.objects.create(
            survey=survey, order=5, maps_to='supporting',
            question_text='What integration benefits do you recognize? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q5, order=1, option_text='🎓 Educational achievement - Second generation excels', 
            card_value='Children of immigrants have higher college graduation rates than native-born Americans')
        QuestionOption.objects.create(question=q5, order=2, option_text='🌎 Cultural diversity strengthens communities', 
            card_value='Immigrant communities enrich American culture and foster global connections')
        QuestionOption.objects.create(question=q5, order=3, option_text='📈 Upward mobility - Immigrants achieve American Dream', 
            card_value='Immigrants demonstrate high rates of business ownership and economic advancement')
        QuestionOption.objects.create(question=q5, order=4, option_text='🏘️ Community revitalization - Immigrants rebuild declining areas', 
            card_value='Immigration has revitalized declining urban and rural communities across America')
        
        # Question 6: Economic Concerns (Opposing)
        q6 = SurveyQuestion.objects.create(
            survey=survey, order=6, maps_to='opposing',
            question_text='What are your economic concerns? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q6, order=1, option_text='💸 Public services strain - Schools, hospitals, infrastructure', 
            card_value='Rapid immigration can strain local public services, schools, and infrastructure in border communities')
        QuestionOption.objects.create(question=q6, order=2, option_text='📉 Wage depression - Impact on low-income Americans', 
            card_value='Studies show immigration can depress wages by 3-8% in affected sectors, harming low-income workers')
        QuestionOption.objects.create(question=q6, order=3, option_text='💰 Fiscal costs - Government benefits and services', 
            card_value='First-generation immigrants may initially use more government services than they contribute in taxes')
        QuestionOption.objects.create(question=q6, order=4, option_text='🏢 Job competition - Displacement of American workers', 
            card_value='Increased labor supply can displace American workers in certain industries and occupations')
        
        # Question 7: Security Concerns (Opposing)
        q7 = SurveyQuestion.objects.create(
            survey=survey, order=7, maps_to='opposing',
            question_text='What security concerns do you have? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q7, order=1, option_text='🔒 Vetting challenges - Cannot properly screen large numbers', 
            card_value='Current immigration volumes make thorough vetting and background checks extremely difficult')
        QuestionOption.objects.create(question=q7, order=2, option_text='🚨 Border control - Losing sovereignty over who enters', 
            card_value='Without secure borders, we cannot control who enters the country or enforce immigration laws')
        QuestionOption.objects.create(question=q7, order=3, option_text='⚖️ Rule of law - Rewarding illegal immigration undermines legal process', 
            card_value='Expanding pathways without enforcement undermines rule of law and fairness to legal immigrants')
        QuestionOption.objects.create(question=q7, order=4, option_text='🎯 Criminal elements - Drug trafficking and gang activity', 
            card_value='Porous borders facilitate drug trafficking, human smuggling, and criminal organizations')
        
        # Question 8: Social Integration Concerns (Opposing)
        q8 = SurveyQuestion.objects.create(
            survey=survey, order=8, maps_to='opposing',
            question_text='What integration challenges concern you? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q8, order=1, option_text='🌍 Cultural assimilation - Language and civic integration', 
            card_value='Large-scale immigration can create integration challenges and language barriers in communities')
        QuestionOption.objects.create(question=q8, order=2, option_text='🏘️ Community cohesion - Rapid demographic changes', 
            card_value='Rapid demographic changes can strain social cohesion and community identity')
        QuestionOption.objects.create(question=q8, order=3, option_text='📚 Education impact - English language learner resources', 
            card_value='High concentrations of non-English speakers strain educational resources and student outcomes')
        QuestionOption.objects.create(question=q8, order=4, option_text='⚡ Infrastructure capacity - Housing and transportation', 
            card_value='Existing infrastructure and housing stock cannot accommodate rapid population increases')
        
        # Question 9: Scope (Federal vs State)
        q9 = SurveyQuestion.objects.create(
            survey=survey, order=9, maps_to='scope',
            question_text='Who should control immigration policy?'
        )
        QuestionOption.objects.create(question=q9, order=1, option_text='🏛️ Federal government - Uniform national policy', card_value='federal')
        QuestionOption.objects.create(question=q9, order=2, option_text='🗺️ State control - Local decisions for local needs', card_value='state')
        QuestionOption.objects.create(question=q9, order=3, option_text='🤝 Federal-state partnership - Shared responsibility', card_value='federal')
        QuestionOption.objects.create(question=q9, order=4, option_text='⚖️ Federal framework with state flexibility', card_value='state')
        
        # Question 10: Solution (Conclusion)
        q10 = SurveyQuestion.objects.create(
            survey=survey, order=10, maps_to='conclusion',
            question_text='What solution would work best? (Select all that apply)'
        )
        QuestionOption.objects.create(question=q10, order=1, option_text='🚀 Expand legal pathways while securing borders', 
            card_value='A balanced approach expanding legal immigration through merit-based and family programs while investing in border security technology and personnel addresses both humanitarian and security needs.')
        QuestionOption.objects.create(question=q10, order=2, option_text='🛡️ Secure borders first, then reform legal system', 
            card_value='Priority must be securing the border and enforcing existing laws before expanding pathways. Once we demonstrate control over illegal immigration, we can have productive discussion about legal reform.')
        QuestionOption.objects.create(question=q10, order=3, option_text='📋 Temporary worker programs tied to economic needs', 
            card_value='Implement robust temporary worker programs responding to labor market demands, allowing immigrants to work legally while maintaining option to return home, providing economic benefits while addressing permanent immigration concerns.')
        QuestionOption.objects.create(question=q10, order=4, option_text='🎯 Points-based system like Canada or Australia', 
            card_value='Adopt a merit-based points system prioritizing skills, education, and economic contribution while maintaining family reunification, providing clear fair criteria balancing economic needs with humanitarian concerns.')
        
        self.stdout.write(self.style.SUCCESS('✅ Immigration survey created with 10 questions!'))
