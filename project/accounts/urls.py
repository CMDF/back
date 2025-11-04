# project/accounts/urls.py

from django.urls import path

# 🚨 [수정] simplejwt에서 TokenVerifyView와 TokenRefreshView를 직접 가져옵니다.
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

# 🚨 [수정] LogoutView는 dj_rest_auth에서 가져옵니다.
from dj_rest_auth.views import LogoutView 

# 🚨 MeView와 GoogleLogin은 accounts.views에서 가져옵니다.
from .views import MeView, GoogleLogin

app_name = "accounts"

urlpatterns = [
    # 1. Google 소셜 로그인/회원가입
    path("google/login/", GoogleLogin.as_view(), name="google_login"),

    # 2. 로그아웃 (dj-rest-auth 뷰)
    path("logout/", LogoutView.as_view(), name="rest_logout"),

    # 3. JWT 토큰 관리 (simplejwt 뷰)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # 4. 프로필 관리 (accounts.views 뷰)
    path("me/", MeView.as_view(), name="me"),
]