# 🏛️ Debrief - Political Argument Database

**Debrief** is a web platform for creating, sharing, and exploring structured political argument cards. Users can take surveys, build argument cards, save research, and engage in evidence-based political discourse.

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.8-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 📊 **Interactive Policy Surveys**
- Take guided surveys on federal and state policy issues
- Answer 10 comprehensive questions with multiple-choice options
- Auto-generate argument cards based on your responses
- Review and edit before publishing

### 💬 **Argument Cards**
- Create structured argument cards with:
  - Hypothesis and conclusion
  - Supporting and opposing arguments
  - Sources and evidence
  - Federal or state scope
  - 40+ policy topics
- Two creation methods:
  - 📊 Survey-based (guided with questions)
  - ✨ Wizard-based (step-by-step form)
- Track argument history with versioning
- Public/private visibility options

### 📓 **Research Notebook**
- Save YouTube videos with auto-transcript extraction
- Bookmark articles with auto-summarization
- Organize by topic, stance, and type
- Add personal notes to entries
- Search across all saved research
- Quick-save bookmarklet for browsers

### 👥 **Social Features**
- Follow other users
- Friend requests and connections
- Direct messaging system
- Share cards via DM
- View user profiles and dashboards
- Real-time notifications

### 🏛️ **Debrief Commons**
- Public argument cards from verified sources
- Synthesize public figure arguments
- Community-driven policy discussions
- Browse by federal vs. state issues

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- PostgreSQL (recommended) or SQLite
- Node.js/npm (for frontend assets, optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/debrief.git
cd debrief
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings:
# - SECRET_KEY
# - DATABASE_URL (if using PostgreSQL)
# - DEBUG=True for development
```

5. **Run migrations**
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

6. **Create superuser**
```bash
python3 manage.py createsuperuser
```

7. **Create Debrief Commons user**
```bash
python3 manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user(username='DebriefCommons', email='commons@debrief.com', password='debrief_commons_2024')
>>> exit()
```

8. **Seed survey data**
```bash
python3 manage.py seed_surveys
```

9. **Run development server**
```bash
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the app!

## 📦 Dependencies

### Core
- **Django 5.2.8** - Web framework
- **django-allauth** - Authentication
- **Pillow** - Image processing

### Features
- **youtube-transcript-api** - Extract YouTube transcripts
- **beautifulsoup4** - Web scraping for articles
- **requests** - HTTP library

### Database
- **psycopg2-binary** - PostgreSQL adapter (production)
- SQLite (development, default)

See `requirements.txt` for full list.

## 🏗️ Project Structure
```
debrief/
├── cards/                      # Main app
│   ├── management/
│   │   └── commands/
│   │       └── seed_surveys.py # Survey data seeding
│   ├── templates/
│   │   └── cards/             # All HTML templates
│   ├── models.py              # Database models
│   ├── views.py               # Main views (cards, notebook, surveys)
│   ├── messaging_views.py     # Messaging & DM views
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   ├── youtube_utils.py       # YouTube transcript utilities
│   └── article_utils.py       # Article scraping utilities
├── debrief/                   # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/                     # User uploads
├── static/                    # Static files
├── requirements.txt           # Python dependencies
└── manage.py                  # Django management script
```

## 🗄️ Database Models

### Core Models
- **Card** - Argument cards with hypothesis, conclusion, stance
- **Argument** - Pro/con arguments for cards
- **Source** - Evidence sources for arguments
- **CardVersion** - Version history tracking

### User & Social
- **UserSettings** - User preferences and profiles
- **Follow** - Follow relationships
- **FriendRequest** - Friend connections
- **Notification** - User notifications

### Messaging
- **Conversation** - DM conversations
- **DirectMessage** - Individual messages

### Notebook
- **NotebookEntry** - Saved research items
- **NotebookNote** - Personal notes on entries

### Surveys
- **TopicSurvey** - Survey definitions
- **SurveyQuestion** - Survey questions
- **QuestionOption** - Multiple choice options

## 🎨 Key Features Detail

### Survey System
Located at `/surveys/`

1. **Browse Surveys** - Filter by federal/state issues
2. **Take Survey** - 10 questions with progress tracking
3. **Auto-Generate Card** - Based on selected answers
4. **Review & Edit** - Preview before publishing
5. **Publish** - Goes live immediately or save as draft

Survey topics match Card topics (immigration, healthcare, education, etc.)

### Notebook System
Located at `/notebook/`

**Features:**
- Quick-save bookmarklet for browser toolbar
- Auto-extract YouTube transcripts (when available)
- Auto-summarize articles (extractive method)
- Organize by topic (12 categories)
- Filter by type (YouTube, Article, Note, Quote)
- Filter by stance (Supporting, Opposing, Neutral)
- Search by title, description, or tags
- Add multiple personal notes per entry

**Workflow:**
1. Click bookmarklet while on YouTube or article
2. Entry auto-saves with extracted content
3. View in notebook with full transcript/summary
4. Add personal notes as you research
5. Reference when creating argument cards

### Argument Cards

**Card Structure:**
- **Title** - Main claim
- **Topic** - Policy area (40+ options)
- **Scope** - Federal or State
- **Stance** - For or Against
- **Hypothesis** - Core reasoning
- **Supporting Arguments** - Pro points with sources
- **Opposing Arguments** - Con points with sources
- **Conclusion** - Final position

**Creation Methods:**
1. **Survey** - Answer questions → auto-generate
2. **Wizard** - Step-by-step guided form
3. **Advanced** - Full form with all fields

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/debrief
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Email Settings (Optional)

For email verification and notifications:
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🚀 Deployment

### Recommended: Render.com

**Why Render?**
- Free tier with PostgreSQL
- GitHub auto-deploy
- No API restrictions (YouTube, web scraping work)
- Easy environment variables
- Automatic SSL certificates

**Steps:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to repository
4. Set environment variables
5. Deploy!

See `render.yaml` for configuration (coming soon).

### Alternative: Railway, Fly.io

Both offer similar features with free tiers and no API restrictions.

**❌ Not Recommended: PythonAnywhere**
- Whitelist restrictions block YouTube API
- Web scraping limited
- External API calls blocked on free tier

## 🛠️ Development

### Running Tests
```bash
python3 manage.py test
```

### Create Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Collect Static Files
```bash
python3 manage.py collectstatic
```

### Create Superuser
```bash
python3 manage.py createsuperuser
```

### Add Survey Topics
```bash
python3 manage.py seed_surveys
```

## 📝 API Endpoints

### Main Routes
- `/` - Home/landing page
- `/dashboard/` - User dashboard
- `/browse/` - Browse all public cards
- `/commons/` - Debrief Commons cards
- `/create/wizard/` - Guided card creation
- `/surveys/` - Survey list
- `/notebook/` - Research notebook
- `/conversations/` - Direct messages

### Card Routes
- `/card/<id>/` - View card detail
- `/card/<id>/edit-forms/` - Edit card
- `/card/<id>/history/` - Version history
- `/card/<id>/save/` - Bookmark card

### Social Routes
- `/user/<username>/` - User profile
- `/follow/<user_id>/` - Follow user
- `/friend-request/send/<user_id>/` - Send friend request
- `/notifications/` - View notifications

## 🎯 Roadmap

### Upcoming Features
- [ ] AI-powered argument generation
- [ ] Debate/discussion threads
- [ ] Card collections and playlists
- [ ] Advanced search with filters
- [ ] Export cards to PDF
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations
- [ ] Automated fact-checking integration
- [ ] Citation management system
- [ ] Collaborative card editing

### Survey Expansion
- [ ] Add more policy topics
- [ ] AI-generated questions based on current events
- [ ] Dynamic question branching
- [ ] Evidence-based question context
- [ ] User-submitted survey topics

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Paul Frendach**
- GitHub: [@alrightyfella](https://github.com/alrightyfella)

## 🙏 Acknowledgments

- Django community for excellent documentation
- YouTube Transcript API for transcript extraction
- Beautiful Soup for web scraping capabilities
- Anthropic Claude for development assistance

## 📧 Support

For support, email support@debrief.com or open an issue on GitHub.

---

**Built with ❤️ for better political discourse**
