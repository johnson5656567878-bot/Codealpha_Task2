# Nexus Social — Modern Full-Stack Social Networking Platform

Nexus is a full-featured, responsive, production-minded social media web application engineered with **Python Django**, **Django REST Framework**, **Vanilla JavaScript**, **HTML5**, **CSS3 / Bootstrap 5**, and **Font Awesome 6**.

Designed with an original visual identity, fluid dark/light theming, micro-interactions, and a normalized relational database architecture.

---

## 🌟 Key Features

### 1. 🔐 Complete Authentication & Account Security
- **User Registration**: Real-time validation for duplicate usernames and emails, password confirmation, and optional avatar upload.
- **Secure Authentication**: Django PBKDF2/Argon2 password hashing, session management, and CSRF token protection on every endpoint.
- **Password Recovery**: Complete password reset flow with email link generation (`PasswordResetView`, token validation, and password confirmation).
- **Settings & Password Update**: Authenticated settings panel allowing users to update their password with current password verification.

### 2. 👤 Dynamic Profile System
- **Profile Customization**: Cover image banner, circular floating avatar, full name, bio, location, and website.
- **Followers & Following Counters**: Dynamically updated counters that trigger an interactive modal displaying lists of followers and following users.
- **Profile Tabs**: Seamlessly toggle between **Posts**, **Media** (posts with images), and **Likes** (posts liked by the user).
- **Ownership Protection**: Only the account owner has access to edit their profile information.

### 3. ✍️ Posts Management & Media Galleries
- **Text & Image Posts**: Create rich posts with captions, automated hashtag detection (`#hashtag`), and user mentions (`@username`).
- **Multiple Image Uploads**: Multi-file picker with real-time thumbnail previews and delete capability before publishing.
- **Responsive Galleries**: Adaptive CSS grid layouts (1, 2, 3, or 4+ images) with an integrated lightbox modal preview.
- **Post Ownership & Moderation**: Authors can edit post text or delete their own posts; non-authors can report inappropriate content or block users.

### 4. ❤️ Heart Like & Bookmark System
- **Real-Time Like Toggle**: Instant heart pulse bounce animation, dynamic like count update, and duplicate like prevention via database unique constraints (`UniqueConstraint(user, post)`).
- **View Who Liked**: Post cards feature a "(view)" trigger opening a modal listing all accounts that liked the post.
- **Bookmarks (Saved Posts)**: Save posts to your personal `/bookmarks/` library for quick reference later.

### 5. 💬 Comments & Replies
- **Interactive Commenting**: Submit comments without page reloads via the Fetch API; immediate insertion into the comments stream.
- **Delete Comments**: Authors can delete their own comments or comments on their posts.
- **Nested Threaded Replies**: Support for replying directly to comments with `@username` pre-population.

### 6. 🤝 Follow & Unfollow Architecture
- **Follow System**: Instant AJAX follow/unfollow toggle with database checks preventing self-follows and duplicate relations.
- **Bidirectional Relationship Updates**: Follower and following counters update automatically for both profiles.
- **Blocked Users Filtering**: Users can block accounts; blocked accounts are immediately filtered out from home feeds, search, and profiles.

### 7. 📰 Algorithmic & Chronological Feeds
- **"For You" Feed**: Global discovery feed of latest community posts.
- **"Following" Feed**: Dedicated chronological stream containing posts exclusively from accounts the user follows plus their own posts.
- **Suggested Accounts ("Who to follow")**: Dynamic sidebar recommendation widget highlighting community members.
- **Trending Topics**: Aggregated hashtags ranked by post volume.

### 8. 🔍 Search & Discovery
- **Global Search**: Search across **Users** (by username and full name), **Posts** (by keyword), and **Hashtags**.
- **Explore Hub**: Dedicated `/explore/` view featuring popular trending posts and active hashtag chips.

### 9. 🔔 In-App Notifications
- **Event Triggers**: Real-time notifications generated when someone likes your post, comments, replies, or follows you.
- **Badge Counter**: Header unread counter badge.
- **Notifications Hub**: Dedicated page to filter by *All*, *Unread*, *Likes*, *Comments*, and *Follows*, with one-click "Mark all as read".

### 10. 🎨 UI/UX & Responsive Design
- **Theme Switcher**: Instant Light / Dark mode toggle with `localStorage` persistence.
- **Responsive Breakpoints**: 3-column desktop layout (Sidebar + Feed + Discovery), collapsed tablet layout, and sticky bottom navigation bar on mobile devices.
- **Custom Error Pages**: Styled 404, 500, and 403 pages.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3 (CSS Variables), Vanilla JavaScript (ES6+), Bootstrap 5.3, Font Awesome 6 |
| **Backend** | Python 3.13, Django 6+, Django REST Framework (DRF) |
| **Database** | SQLite (development) / PostgreSQL (production ready via psycopg2) |
| **Media Handling** | Pillow (PIL) for image verification and processing |
| **Environment** | python-dotenv for environment variables |

---

## 📁 Project Structure

```
codealpha2/
├── manage.py
├── requirements.txt
├── .env.example
├── .env
│
├── config/                  # Django project configuration
│   ├── settings.py          # Settings, DRF config, static/media paths
│   ├── urls.py              # Root routing & custom error handlers
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # Authentication, UserProfile & Settings
│   ├── models.py            # UserProfile model
│   ├── forms.py             # UserRegistrationForm, UserProfileEditForm
│   ├── views.py             # Login, Register, Logout, Profile, Settings
│   ├── urls.py
│   ├── signals.py           # Auto-creates UserProfile on User save
│   ├── context_processors.py# Current user profile provider
│   └── management/commands/
│       └── seed_demo_data.py# Seeds realistic users, posts & media
│
├── posts/                   # Posts, Images, Likes, Comments, Follows, Tags
│   ├── models.py            # Post, PostImage, Like, Comment, Follow, Bookmark, Hashtag, Report, Block
│   ├── views.py             # Feed, Explore, Search, Bookmarks, and REST API handlers
│   └── urls.py
│
├── notifications/           # In-app notifications engine
│   ├── models.py            # Notification model & create_notification utility
│   ├── views.py             # Notifications page & unread mark API
│   ├── urls.py
│   └── context_processors.py# Unread notifications count
│
├── templates/
│   ├── base.html            # Main layout with modals, alerts, and theme switcher
│   ├── home.html            # Main feed & compose post card
│   ├── explore.html         # Explore hub with trending tags
│   ├── search.html          # Multi-tab search interface
│   ├── bookmarks.html       # Saved posts view
│   ├── notifications.html   # Notifications center
│   ├── includes/
│   │   ├── sidebar.html     # Desktop left navigation
│   │   ├── right_sidebar.html # Suggested users & trends
│   │   ├── mobile_nav.html  # Mobile bottom dock
│   │   └── post_card.html   # Reusable post card with interactive actions
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── password_reset.html
│   │   ├── password_reset_done.html
│   │   ├── password_reset_confirm.html
│   │   └── password_reset_complete.html
│   ├── profiles/
│   │   ├── profile.html     # User profile header, stats, and tabs
│   │   └── settings.html    # Profile & password settings
│   ├── posts/
│   │   ├── post_detail.html # Dedicated post view & comments
│   │   └── hashtag_posts.html
│   └── errors/
│       ├── 404.html
│       ├── 500.html
│       └── 403_blocked.html
│
├── static/
│   ├── css/styles.css       # Complete custom design system
│   ├── js/app.js            # CSRF, Theme, Follow, Notifications JS
│   ├── js/posts.js          # Post compose, Likes, Comments, Lightbox JS
│   └── images/              # SVG brand logos & default avatars
│
└── media/                   # User uploaded avatars, covers, and post photos
```

---

## 🚀 Quickstart & Installation

### 1. Clone or Open Workspace
```bash
cd codealpha2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment File
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Realistic Demo Data (Optional but Recommended)
Populates the database with realistic creator profiles, posts with generated images, comments, likes, and followers:
```bash
python manage.py seed_demo_data
```

### 6. Run the Automated Test Suite
```bash
python manage.py test
```

### 7. Start the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

---

## 🔑 Pre-Configured Demo Credentials

If you ran `python manage.py seed_demo_data`, you can instantly log in with:

| Account Type | Username | Password | Notes |
|---|---|---|---|
| **Demo User** | `demo_user` | `demopassword123` | Standard user with pre-seeded feed, posts, and bookmarks |
| **Creator** | `alex_design` | `password123` | Product Designer with UI posts |
| **Creator** | `sophia_tech` | `password123` | Backend Engineer with technical posts |
| **Administrator** | `admin` | `admin123456` | Full Django Admin superuser (`/admin/`) |

You can also register a brand new account anytime via **`/accounts/register/`**.
