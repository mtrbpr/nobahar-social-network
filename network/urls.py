from django.urls import path
from rest_framework import routers

from network.views import SignupAPIView, LoginAPIView, GroupAPIViewSet, JoinRequestAPIViewSet, \
    ConnectionRequestAPIViewSet, chat_view, all_chats_view

router = routers.DefaultRouter()
router.register(r'groups', GroupAPIViewSet, basename='groups')
router.register(r'join_requests', JoinRequestAPIViewSet, basename='join_requests')
router.register(r'connection_requests', ConnectionRequestAPIViewSet, basename='connection_requests')

urlpatterns = [
    path('auth/signup/', SignupAPIView.as_view(), name='signup'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('chats/<int:user_id>/', chat_view, name='chats'),
    path('chats/', all_chats_view, name='chats-all'),
] + router.urls

