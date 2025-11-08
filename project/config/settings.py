from pathlib import Path
import os, json
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = os.path.join(BASE_DIR, 'secrets.json') 

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets): 
# secret 변수를 가져오거나 그렇지 못 하면 예외를 반환
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_secret("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites'
]

PROJECT_APPS = [
    'accounts',
    'pdf_documents',
    'pdf_figures',
    'highlights'
]

THIRD_PARTY_APPS = [
    "corsheaders",
    # DRF를 위한 패키지
    "rest_framework",
    # JWT를 위한 패키지
    'rest_framework_simplejwt',

    "dj_rest_auth",
    "dj_rest_auth.registration",
    # OAuth를 위한 패키지
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # 다양한 스토리지를 사용하기 위한 패키지
    "storages",
    # swagger를 위한 패키지
    "drf_yasg",

    "rest_framework_simplejwt.token_blacklist"
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 미들웨어를 맨 위에 추가
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", # allauth 미들웨어
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Database (로컬 테스트 용)
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DB_PW = get_secret("DB_PW")
RDS_HOST = get_secret("RDS_HOST")
RDS_PORT = get_secret("RDS_PORT")
RDS_DB_NAME = get_secret("RDS_DB_NAME")
RDS_USERNAME = get_secret("RDS_USERNAME")
RDS_PASSWORD = get_secret("RDS_PASSWORD")
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': RDS_DB_NAME,
		'USER': RDS_USERNAME,
		'PASSWORD': RDS_PASSWORD,
		'HOST': RDS_HOST,
		'PORT': RDS_PORT,
	}
}

# 로컬 테스트용
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# 타임존을 서울로 변경
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 인증 관련 요청(쿠키, 세션 등)을 허용
# 예를 들어 브라우저가 백엔드 서버로 쿠키를 전송하거나, 백엔드에서 쿠키를 응답으로 보낼 수 있음
CORS_ALLOW_CREDENTIALS = True

# 서버로 요청 보낼 수 있는 도메인들 정의
# 여기에서의 localhost는 EC2 인스턴스의 로컬환경이 아니라 프론트엔드 개발 로컬 환경 의미
# 3000 포트는 프론트엔드 React 애플리케이션의 포트 번호
# 추후 프론트엔드에서 웹 페이지 배포 후 도메인 매핑했다면 해당 도메인 추가 필요
CORS_ALLOWED_ORIGINS = [ 
]

# DRF (Django Rest Framework) 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # API 요청 시 인증을 위해 'simplejwt'의 JWT 인증을 사용
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# REST_USE_JWT = True

# REST_AUTH_TOKEN_MODEL = None

# # JWT가 HTTP 헤더가 아닌 쿠키를 통해 전송되도록 설정 (API 서버-클라이언트 방식이므로 False)
# # dj-rest-auth 기본값은 False이지만 명시적으로 설정
# JWT_AUTH_COOKIE = None 
# JWT_AUTH_REFRESH_COOKIE = None

# ----- dj-rest-auth v5 설정 -----
REST_AUTH = {
    # 토큰 모델을 끄면 authtoken을 요구하지 않음
    'TOKEN_MODEL': None,
    'REST_SESSION_LOGIN': False,
    # JWT 사용
    'USE_JWT': True,

    # (쿠키를 안 쓸 거면 None 유지)
    # 'JWT_AUTH_COOKIE': None,
    # 'JWT_AUTH_REFRESH_COOKIE': None,

    "JWT_AUTH_COOKIE": "access_token",
    "JWT_AUTH_REFRESH_COOKIE": "refresh_token",
    "JWT_AUTH_HTTPONLY": False,
    # 필요하면 여기에 다른 옵션들도 REST_AUTH 안에 넣습니다.
}



# allauth가 사용하는 기본 사이트 ID. (django.contrib.sites 앱이 필요함)
# DJANGO_APPS에 'django.contrib.sites'를 추가해야 합니다.
SITE_ID = 1

# allauth 관련 설정
# ------------------------------------------------
# 인증 백엔드: Django 기본 인증 + allauth 이메일 인증
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # Django 기본 인증
    'allauth.account.auth_backends.AuthenticationBackend', # allauth 인증
)

# 소셜 로그인 시 이메일 주소는 필수로 받음
SOCIALACCOUNT_EMAIL_REQUIRED = True
# 소셜 로그인 시 사용자에게 별도로 이메일 확인을 받지 않음 (개발 편의성)
ACCOUNT_EMAIL_VERIFICATION = 'none' 
# 사용자 이름(username) 대신 이메일을 ID로 사용
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False # username 필드를 사용하지 않음
ACCOUNT_USER_MODEL_USERNAME_FIELD = None # username 필드를 사용하지 않음


# Google 소셜 로그인 관련 설정
# ------------------------------------------------
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            # 🔑 이 부분은 secrets.json에서 불러오도록 수정하세요.
            'client_id': get_secret("GOOGLE_CLIENT_ID"),
            'secret': get_secret("GOOGLE_CLIENT_SECRET"),
        },
        'SCOPE': [ # Google로부터 요청할 사용자 정보 범위
            'openid',
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    }
}


SIMPLE_JWT = {
    # 1. 우리가 사용할 기본 키 필드 지정 (기본값: 'id')
    'USER_ID_FIELD': 'user_id',
    
    # 2. JWT 토큰의 "user_id" 클레임 이름 (기본값: 'user_id')
    'USER_ID_CLAIM': 'user_id', # 이것도 user_id로 명시

    # 3. 토큰 유효 시간 설정 (선택 사항이지만 권장)
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),   # Access Token 유효 시간 (예: 1시간)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # Refresh Token 유효 시간 (예: 7일)
    
    # 4. 기타 설정
    'AUTH_HEADER_TYPES': ('Bearer',), # 인증 헤더 타입 (Bearer <token>)
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION', # 인증 헤더 이름
}

###AWS###
AWS_ACCESS_KEY_ID = get_secret("AWS_ACCESS_KEY_ID") # .csv 파일에 있는 내용을 입력 Access key ID. IAM 계정 관련
AWS_SECRET_ACCESS_KEY = get_secret("AWS_SECRET_ACCESS_KEY") # .csv 파일에 있는 내용을 입력 Secret access key. IAM 계정 관련
AWS_REGION = 'ap-northeast-2'

###S3###
AWS_STORAGE_BUCKET_NAME = get_secret("AWS_STORAGE_BUCKET_NAME")
#AWS_S3_CUSTOM_DOMAIN = '%s.s3.%s.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,AWS_REGION)
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}


SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT 토큰 입력. 예) "Bearer <access_token>"',
        }
    },
    "USE_SESSION_AUTH": False,  # 세션 인증 버튼 비표시 (JWT만 쓸 때 권장)
}