import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['vibecityrp.com', 'www.vibecityrp.com', '204.10.193.192', 'localhost', '127.0.0.1', 'https://vibecityrp.com']

CSRF_TRUSTED_ORIGINS = [
    'https://vibecityrp.com',
    'https://www.vibecityrp.com',
    'http://204.10.193.192',
    'http://localhost:8000',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'crispy_forms',
    'crispy_tailwind',
    'social_django',
    'tailwind',
    
    # Local apps
    'accounts',
    'whitelist',
    'dashboard',
    'jobs',
    'guidebook',
    'keybinds',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'vibe_city_rp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'vibe_city_rp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
# }

# Authentication
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.discord.DiscordOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'accounts.pipeline.set_auth_time',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


# Discord OAuth2 settings
# Existing
SOCIAL_AUTH_DISCORD_KEY = os.getenv('DISCORD_CLIENT_ID')
SOCIAL_AUTH_DISCORD_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
SOCIAL_AUTH_DISCORD_SCOPE = ['identify']

# Add this — ensures refresh_token is always included
SOCIAL_AUTH_DISCORD_AUTH_EXTRA_ARGUMENTS = {
    'prompt': 'consent'
}

# Optional but useful — store token expiration & refresh_token
SOCIAL_AUTH_DISCORD_EXTRA_DATA = ['refresh_token', 'expires_in']

# Redirects
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/accounts/profile/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/accounts/login/'
SOCIAL_AUTH_LOGOUT_REDIRECT_URL = '/'

SOCIAL_AUTH_DISCORD_TOKEN_EXPIRATION = True
SOCIAL_AUTH_REFRESH_TOKEN_EXPIRATION = True


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Tailwind CSS
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1",
]

# Discord Bot settings
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID')
DISCORD_WHITELIST_ROLE_ID=1356155801164845148
DISCORD_APPLICATIONS_CHANNEL_ID=1223699596035756144
DISCORD_WHITELIST_RESPONSES_CHANNEL_ID=1356158346260123790
DISCORD_NOTIFICATIONS_CHANNEL_ID=1223699596035756144
DISCORD_JOB_APPLICATIONS_CHANNEL_ID=1223699596035756144
DISCORD_JOB_RESPONSES_CHANNEL_ID=1355258731906072757
DISCORD_SUPPORT_CHANNEL_ID=1223699596035756144
DISCORD_WELCOME_CHANNEL_ID=1315378708860637204

# Discord Role IDs for Job Applications
DISCORD_SASP_INTERVIEW_ROLE_ID = '1365759489231552572'  # Replace with actual SASP Interview role ID
DISCORD_SASP_HIRED_ROLE_ID = '1365759699378770121'      # Replace with actual SASP Hired role ID
DISCORD_EMS_INTERVIEW_ROLE_ID = '1365759489231552572'   # Replace with actual EMS Interview role ID
DISCORD_EMS_HIRED_ROLE_ID = '1365759756005937273'       # Replace with actual EMS Hired role ID
DISCORD_MECHANIC_INTERVIEW_ROLE_ID = '1365759489231552572'  # Replace with actual Mechanic Interview role ID
DISCORD_MECHANIC_HIRED_ROLE_ID = '1356161401449746573'      # Replace with actual Mechanic Hired role ID