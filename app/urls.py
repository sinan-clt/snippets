from django.urls import path
from app.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('register', Register.as_view(), name='register_user'),
    path('login', UserLogin.as_view(), name='login_user'),
    path('user_details', authenticatedUserDetails.as_view(), name='user_details'),

    path('overview/', OverviewAPI.as_view(), name='snippet_overview'),
    path('create/', CreateAPI.as_view(), name='snippet_create'),
    path('detail/<int:snippet_id>/', DetailAPI.as_view(), name='snippet_detail'),
    path('update/<int:snippet_id>/', UpdateAPI.as_view(), name='snippet_update'),
    path('delete/<int:snippet_id>/', DeleteAPI.as_view(), name='snippet_delete'),
    path('tag/list/', TagListAPI.as_view(), name='tag_list'),
    path('tag/detail/<int:tag_id>/', TagDetailAPI.as_view(), name='tag_detail'),

]

