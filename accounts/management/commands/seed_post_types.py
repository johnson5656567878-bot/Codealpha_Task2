import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from posts.models import Post, PollOption, PollVote


class Command(BaseCommand):
    help = 'Adds diverse post types: Interactive Polls, Code Snippets, and Announcements'

    def handle(self, *args, **options):
        self.stdout.write("Adding diverse post types...")

        # 1. Interactive Poll Post by alex_design
        alex = User.objects.get(username='alex_design')
        p1, _ = Post.objects.get_or_create(
            author=alex,
            content="Community pulse check! 🎨 When designing responsive web layouts in 2026, what's your primary CSS layout strategy? Vote below! #webdev #css #design #frontend",
            defaults={
                'post_type': 'poll',
                'poll_question': 'What is your primary CSS layout strategy?'
            }
        )
        p1.post_type = 'poll'
        p1.poll_question = 'What is your primary CSS layout strategy?'
        p1.save()
        if not p1.poll_options.exists():
            opt1 = PollOption.objects.create(post=p1, text='CSS Grid (Modern 2D Layouts)', order=0)
            opt2 = PollOption.objects.create(post=p1, text='Flexbox (Row and column alignment)', order=1)
            opt3 = PollOption.objects.create(post=p1, text='Subgrid and Container Queries', order=2)
            opt4 = PollOption.objects.create(post=p1, text='Utility CSS (Tailwind / Bootstrap)', order=3)

            users = list(User.objects.exclude(username='alex_design')[:6])
            if len(users) >= 4:
                PollVote.objects.get_or_create(post=p1, user=users[0], defaults={'option': opt1})
                PollVote.objects.get_or_create(post=p1, user=users[1], defaults={'option': opt1})
                PollVote.objects.get_or_create(post=p1, user=users[2], defaults={'option': opt2})
                PollVote.objects.get_or_create(post=p1, user=users[3], defaults={'option': opt3})

        # 2. Code Snippet Post by sophia_tech
        sophia = User.objects.get(username='sophia_tech')
        code_content = """import threading

class CachedProperty:
    \"\"\"Thread-safe atomic memoization descriptor.\"\"\"
    def __init__(self, func):
        self.func = func
        self.lock = threading.Lock()
        self.name = func.__name__

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        with self.lock:
            if self.name not in instance.__dict__:
                instance.__dict__[self.name] = self.func(instance)
            return instance.__dict__[self.name]"""

        p2, _ = Post.objects.get_or_create(
            author=sophia,
            content="Here is a clean pattern for implementing a thread-safe memoized property in Python. Notice how we use atomic check-and-set to avoid redundant database calls. ⚡ #python #cleancode #backend #django",
            defaults={
                'post_type': 'code',
                'code_language': 'python',
                'code_snippet': code_content
            }
        )
        p2.post_type = 'code'
        p2.code_language = 'python'
        p2.code_snippet = code_content
        p2.save()

        # 3. Milestone Announcement by david_startup
        david = User.objects.get(username='david_startup')
        p3, _ = Post.objects.get_or_create(
            author=david,
            content="We just crossed $250k ARR on our bootstrapped SaaS product! 🚀 It took 18 months of relentless execution, but seeing organic word-of-mouth accelerate is the ultimate reward. Huge thank you to the Nexus community for all the early feedback! #startup #saas #milestone #buildinpublic",
            defaults={
                'post_type': 'announcement',
                'badge_text': '🚀 $250K ARR Milestone Achieved',
                'badge_icon': 'fa-trophy'
            }
        )
        p3.post_type = 'announcement'
        p3.badge_text = '🚀 $250K ARR Milestone Achieved'
        p3.badge_icon = 'fa-trophy'
        p3.save()

        # 4. Vector Database Poll by liam_ai
        liam = User.objects.get(username='liam_ai')
        p4, _ = Post.objects.get_or_create(
            author=liam,
            content="Question for engineers and data practitioners: Which vector database or similarity search backend do you rely on most in production? #ai #datascience #database #tech",
            defaults={
                'post_type': 'poll',
                'poll_question': 'Favorite Vector Database for LLMs and RAG?'
            }
        )
        p4.post_type = 'poll'
        p4.poll_question = 'Favorite Vector Database for LLMs and RAG?'
        p4.save()
        if not p4.poll_options.exists():
            v1 = PollOption.objects.create(post=p4, text='pgvector (PostgreSQL extension)', order=0)
            v2 = PollOption.objects.create(post=p4, text='Qdrant / Milvus (Dedicated engines)', order=1)
            v3 = PollOption.objects.create(post=p4, text='Pinecone / Chroma (Cloud Serverless)', order=2)

            users = list(User.objects.exclude(username='liam_ai')[:5])
            if len(users) >= 3:
                PollVote.objects.get_or_create(post=p4, user=users[0], defaults={'option': v1})
                PollVote.objects.get_or_create(post=p4, user=users[1], defaults={'option': v1})
                PollVote.objects.get_or_create(post=p4, user=users[2], defaults={'option': v2})

        # 5. CSS Grid Snippet by elena_dev
        elena = User.objects.get(username='elena_dev')
        css_code = """.responsive-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  align-items: stretch;
}"""

        p5, _ = Post.objects.get_or_create(
            author=elena,
            content="Quick CSS tip! You can create an intrinsically responsive card grid without writing a single media query breakpoint using minmax() and repeat(auto-fit). 📐 #css #webdev #frontend #tips",
            defaults={
                'post_type': 'code',
                'code_language': 'html',
                'code_snippet': css_code
            }
        )
        p5.post_type = 'code'
        p5.code_language = 'html'
        p5.code_snippet = css_code
        p5.save()

        # 6. Hiring Announcement by demo_user
        demo = User.objects.get(username='demo_user')
        p6, _ = Post.objects.get_or_create(
            author=demo,
            content="We are officially expanding our design engineering team at Nexus Studio! If you love crafting high-craft web applications with Django and modern frontend, check out our careers page or DM me directly. 💼✨ #hiring #jobalert #remote #developer",
            defaults={
                'post_type': 'announcement',
                'badge_text': "💼 We're Hiring Designers and Devs",
                'badge_icon': 'fa-briefcase'
            }
        )
        p6.post_type = 'announcement'
        p6.badge_text = "💼 We're Hiring Designers and Devs"
        p6.badge_icon = 'fa-briefcase'
        p6.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded diverse post types!"))
