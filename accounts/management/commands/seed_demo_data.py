import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw

from accounts.models import UserProfile
from posts.models import Post, PostImage, Like, Comment, Follow, Hashtag
from notifications.models import create_notification


def generate_sample_image(text, bg_color1, bg_color2, width=800, height=520):
    """Generates an aesthetic gradient image with geometric accents and text overlay using Pillow."""
    img = Image.new('RGB', (width, height), bg_color1)
    draw = ImageDraw.Draw(img)

    # Draw gradient lines
    r1, g1, b1 = bg_color1
    r2, g2, b2 = bg_color2
    for y in range(height):
        ratio = y / height
        nr = int(r1 * (1 - ratio) + r2 * ratio)
        ng = int(g1 * (1 - ratio) + g2 * ratio)
        nb = int(b1 * (1 - ratio) + b2 * ratio)
        draw.line([(0, y), (width, y)], fill=(nr, ng, nb))

    # Draw decorative geometric elements
    draw.ellipse([width - 180, -60, width + 100, 220], outline=(255, 255, 255, 45), width=3)
    draw.ellipse([-80, height - 200, 160, height + 80], outline=(255, 255, 255, 35), width=4)
    draw.line([60, height - 80, width - 60, height - 80], fill=(255, 255, 255, 50), width=2)

    # Save to BytesIO buffer
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=90)
    clean_name = text.lower().replace(' ', '_').replace('/', '_').replace('-', '_')[:30]
    return ContentFile(buf.getvalue(), name=f"{clean_name}.jpg")


class Command(BaseCommand):
    help = 'Seeds database with realistic creators, rich posts, media images, likes, and comments'

    def handle(self, *args, **options):
        self.stdout.write("Seeding comprehensive realistic social media demo data...")

        # 1. Admin Superuser
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@nexus.local', 'first_name': 'Nexus', 'last_name': 'Admin'}
        )
        if created:
            admin.set_password('admin123456')
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            admin.profile.bio = "Official Administrator of the Nexus Social Platform."
            admin.profile.location = "San Francisco, CA"
            admin.profile.save()

        # 2. Demo User for user testing
        demo_user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@nexus.local', 'first_name': 'Jordan', 'last_name': 'Taylor'}
        )
        if created:
            demo_user.set_password('demopassword123')
            demo_user.save()
            demo_user.profile.bio = "Exploring Nexus! Tech enthusiast, minimalist designer, and coffee drinker. #tech #vibes"
            demo_user.profile.location = "Seattle, WA"
            demo_user.profile.website = "https://jordantaylor.dev"
            demo_user.profile.save()

        # 3. Community Creators
        creators_data = [
            {
                'username': 'alex_design',
                'name': 'Alex Rivera',
                'email': 'alex@nexus.local',
                'bio': 'Lead Product Designer & UI Architect. Building interfaces that delight and inspire. 🎨 ✨ #design #uiux #creativity',
                'location': 'New York, NY',
                'website': 'https://alexrivera.design',
            },
            {
                'username': 'sophia_tech',
                'name': 'Sophia Chen',
                'email': 'sophia@nexus.local',
                'bio': 'Senior Backend & ML Engineer. Obsessed with distributed systems, clean code, and open source. 💻 ☕ #python #django #coding',
                'location': 'San Francisco, CA',
                'website': 'https://sophiachen.io',
            },
            {
                'username': 'marcus_travel',
                'name': 'Marcus Vance',
                'email': 'marcus@nexus.local',
                'bio': 'Landscape & Street Photographer. Traveling the world one mountain and coastline at a time. 📷 🌍 #photography #travel #adventure',
                'location': 'Reykjavik, Iceland',
                'website': 'https://marcusvance.photo',
            },
            {
                'username': 'elena_dev',
                'name': 'Elena Rostova',
                'email': 'elena@nexus.local',
                'bio': 'Full-stack software architect & writer. Turning complex problems into simple, elegant apps. #developer #tech #productivity',
                'location': 'London, UK',
                'website': 'https://elenarostova.dev',
            },
            {
                'username': 'liam_ai',
                'name': 'Liam Patel',
                'email': 'liam@nexus.local',
                'bio': 'Machine Learning Researcher & Engineer. Exploring transformers, diffusion models, and AI reasoning. 🧠 ⚡ #ai #ml #datascience',
                'location': 'Boston, MA',
                'website': 'https://liampatel.ai',
            },
            {
                'username': 'maya_culinary',
                'name': 'Maya Lin',
                'email': 'maya@nexus.local',
                'bio': 'Chef, culinary storyteller, and sourdough enthusiast. Exploring food culture around the globe. 🍜 🥐 #food #culinary #recipes',
                'location': 'Vancouver, Canada',
                'website': 'https://mayacooks.com',
            },
            {
                'username': 'david_startup',
                'name': 'David K.',
                'email': 'david@nexus.local',
                'bio': 'Bootstrapping software to $1M ARR. Building in public, writing about SaaS, remote work, and product strategy. 🚀 #startup #saas #buildinpublic',
                'location': 'Austin, TX',
                'website': 'https://davidk.io',
            }
        ]

        created_users = [demo_user]
        for c in creators_data:
            user, u_created = User.objects.get_or_create(
                username=c['username'],
                defaults={'email': c['email']}
            )
            if u_created:
                parts = c['name'].split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
                user.set_password('password123')
                user.save()
                user.profile.bio = c['bio']
                user.profile.location = c['location']
                user.profile.website = c['website']
                user.profile.save()
            created_users.append(user)

        # 4. Create Follows (Follow web)
        for u in created_users:
            for target in created_users:
                if u != target:
                    Follow.objects.get_or_create(follower=u, following=target)

        # 5. Expanded Rich Posts List
        posts_data = [
            {
                'author': 'alex_design',
                'content': "Just wrapped up the design system overhaul for our upcoming application! 🚀 Focused on accessible contrast, fluid typography, and micro-interactions that feel buttery smooth.\n\nWhat's your take on dark mode vs light mode defaults? #design #uiux #webdev #branding",
                'images': [
                    ("Design System Colors", (79, 70, 229), (147, 51, 234))
                ]
            },
            {
                'author': 'liam_ai',
                'content': "Just published our deep dive on Attention mechanisms in multi-modal LLMs! 🧠 We mapped attention weights across 50,000 image-text pairs. The emergent visual reasoning patterns are mind-blowing.\n\nWhat's your current favorite open-weight vision model? #ai #machinelearning #datascience #research #tech",
                'images': [
                    ("Attention Maps Heatmap", (139, 92, 246), (236, 72, 153)),
                    ("Multi-Modal Benchmarks", (59, 130, 246), (16, 185, 129))
                ]
            },
            {
                'author': 'marcus_travel',
                'content': "First sunrise of the season over the fjords. Nothing beats the crisp morning silence and the golden glow reflecting off the glacial water. 🏔️✨ #travel #photography #adventure #nature #wanderlust",
                'images': [
                    ("Nordic Fjords Sunrise", (249, 115, 22), (236, 72, 153))
                ]
            },
            {
                'author': 'maya_culinary',
                'content': "Sunday morning sourdough ritual: 80% hydration, 24-hour cold ferment, and baked in a preheated cast iron combo cooker at 240°C. 🍞\n\nThe ear and oven spring turned out heavenly today! Who else bakes their own bread? #food #baking #sourdough #homemade #culinary",
                'images': [
                    ("Artisan Sourdough Loaf", (217, 119, 6), (180, 83, 9)),
                    ("Open Crumb Structure", (245, 158, 11), (217, 119, 6)),
                    ("Golden Crust Close-up", (180, 83, 9), (120, 53, 15))
                ]
            },
            {
                'author': 'sophia_tech',
                'content': "Migrated our core database architecture to optimized query sets with prefetch_related and select_related. Result? Latency dropped from 240ms to under 18ms! ⚡ \n\nNever underestimate the power of profiling before optimizing. #python #django #coding #performance #backend",
                'images': [
                    ("Database Query Benchmarks", (16, 185, 129), (6, 182, 212))
                ]
            },
            {
                'author': 'david_startup',
                'content': "10 lessons from bootstrapping our SaaS product to 10,000 active users with zero VC funding:\n\n1. Solve an immediate hair-on-fire problem.\n2. Talk to 5 customers every single week.\n3. Ship weekly, iterate relentlessly.\n4. Simplicity wins over endless feature lists.\n5. Distribution is just as crucial as engineering.\n\nKeep building! 🚀 #buildinpublic #startup #saas #entrepreneur #growth",
                'images': []
            },
            {
                'author': 'alex_design',
                'content': "Exploring ambient lighting and subtle glassmorphism for dashboard cards. ✨ When used with high-contrast typography, frosted glass creates such a refined sense of depth without overwhelming the eye. #design #uiux #dashboard #figma #minimalism",
                'images': [
                    ("Glassmorphism Dashboard UI", (99, 102, 241), (168, 85, 247))
                ]
            },
            {
                'author': 'marcus_travel',
                'content': "Lost in the neon-lit alleys of Shinjuku, Tokyo after a sudden evening downpour. 🌧️ Reflections on wet asphalt always make the city feel alive like a cyberpunk movie set. #tokyo #japan #streetphotography #travel #nightphotography #cyberpunk",
                'images': [
                    ("Shinjuku Neon Rain", (236, 72, 153), (79, 70, 229)),
                    ("Omoide Yokocho Alley", (239, 68, 68), (249, 115, 22)),
                    ("Reflections on Wet Asphalt", (59, 130, 246), (147, 51, 234)),
                    ("Tokyo Subway Entrance", (16, 185, 129), (59, 130, 246))
                ]
            },
            {
                'author': 'elena_dev',
                'content': "Pro tip for developers: If you find yourself writing repetitive validation logic, abstract it into clean domain decorators or reusable validator functions. Keep your views razor thin! 💡 #developer #tech #productivity #cleancode",
                'images': []
            },
            {
                'author': 'liam_ai',
                'content': "Prompt engineering vs Fine-tuning: In 2026, prompt context caching and structured JSON outputs have made 90% of routine fine-tuning redundant. Save your compute budget for genuine domain adaptation! #ai #ml #tech #software",
                'images': []
            },
            {
                'author': 'demo_user',
                'content': "Morning cycling tour along the waterfront trail! Perfect weather and a crisp breeze. Starting the day with fresh energy! 🚴‍♂️🌅 #cycling #morning #fitness #lifestyle #outdoors #vibes",
                'images': [
                    ("Waterfront Trail Sunrise", (249, 115, 22), (234, 88, 12)),
                    ("Bicycle by the Pier", (59, 130, 246), (99, 102, 241))
                ]
            },
            {
                'author': 'maya_culinary',
                'content': "Handmade matcha ramen with black garlic oil and slow-poached eggs. Food is art, science, and comfort all in one steaming bowl. 🍜 #culinary #foodie #ramen #japanesefood #homemade",
                'images': [
                    ("Matcha Black Garlic Ramen", (16, 185, 129), (180, 83, 9))
                ]
            },
            {
                'author': 'sophia_tech',
                'content': "Clean code tip: Avoid nested ternary operators and long if-else ladders. Using dictionary dispatch or Python pattern matching makes your domain logic so much more readable and testable. 💡 #python #programming #cleancode #developer #tips",
                'images': []
            },
            {
                'author': 'david_startup',
                'content': "Your first version will always make you cringe a bit, and that's completely okay. If you're not slightly embarrassed by v1.0, you launched too late. Get real user feedback as early as possible. #startup #buildinpublic #founder #advice",
                'images': []
            },
            {
                'author': 'marcus_travel',
                'content': "The Milky Way arching over the desert sand dunes in Atacama, Chile. 🌌 One of the darkest skies on planet Earth. 25-second exposure, f/2.8, ISO 3200. #astrophotography #milkyway #space #travel #landscape",
                'images': [
                    ("Atacama Desert Night Sky", (30, 27, 75), (88, 28, 135))
                ]
            },
            {
                'author': 'elena_dev',
                'content': "Building with Vanilla JavaScript and modern CSS feels so liberating. No massive node_modules dependencies, zero build step lag, instant refresh. Browsers in 2026 are extraordinarily capable! ⚡ #javascript #webdev #frontend #performance",
                'images': []
            },
            {
                'author': 'demo_user',
                'content': "Loving the new responsive layout on Nexus! The dark mode toggle and real-time heart animations are so smooth. Great community here! ✨ #nexus #community #social #vibes",
                'images': [
                    ("Nexus Social Aesthetic", (99, 102, 241), (236, 72, 153))
                ]
            }
        ]

        created_posts = []
        for pdata in posts_data:
            author_user = User.objects.get(username=pdata['author'])
            post, p_created = Post.objects.get_or_create(
                author=author_user,
                content=pdata['content']
            )
            if p_created and pdata.get('images'):
                for img_title, c1, c2 in pdata['images']:
                    img_file = generate_sample_image(img_title, c1, c2)
                    PostImage.objects.create(post=post, image=img_file)
            created_posts.append(post)

        # 6. Create Varied Likes & Comments
        sample_comments = [
            ("Great insights! The attention to detail really shows.", 'sophia_tech'),
            ("Stunning visuals! What camera lens did you use for this shot?", 'alex_design'),
            ("Totally agree on keeping views thin and logic modular.", 'demo_user'),
            ("Welcome to Nexus! Excited to see your upcoming posts.", 'elena_dev'),
            ("This is brilliantly explained. Sharing with our team!", 'david_startup'),
            ("The color harmony here is absolutely sublime.", 'maya_culinary'),
            ("Fascinating analysis! Looking forward to the followup.", 'liam_ai'),
            ("Bookmarked for later reference. Keep inspiring!", 'marcus_travel'),
        ]

        import random
        for idx, post in enumerate(created_posts):
            # Select 3-6 random users to like this post
            likers = [u for u in created_users if u != post.author]
            num_likes = min(len(likers), 3 + (idx % 4))
            chosen_likers = likers[:num_likes]

            for u in chosen_likers:
                like, l_created = Like.objects.get_or_create(user=u, post=post)
                if l_created:
                    create_notification(recipient=post.author, sender=u, notification_type='like', post=post)

            # Add 1-3 comments
            num_comments = 1 + (idx % 3)
            for c_idx in range(num_comments):
                text, commenter_uname = sample_comments[(idx + c_idx) % len(sample_comments)]
                c_user = User.objects.get(username=commenter_uname)
                if c_user != post.author:
                    c, c_created = Comment.objects.get_or_create(post=post, author=c_user, content=text)
                    if c_created:
                        create_notification(recipient=post.author, sender=c_user, notification_type='comment', post=post, comment=c)

        self.stdout.write(self.style.SUCCESS(f"Successfully populated {len(created_posts)} rich posts with images, comments, and likes!"))
