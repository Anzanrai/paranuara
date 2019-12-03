from django.urls import path, include
from rest_framework import routers

from .views import CompanyViewSet, EmployeeViewSet, common_friend_view

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'employees', EmployeeViewSet, basename='employees')

urlpatterns = [
    path('', include(router.urls)),
    path(r'common-friends/', common_friend_view)
]
