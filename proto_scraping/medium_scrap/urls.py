
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.signup_user, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('tags_query/<str:tag>/<int:page>',views.tags_query,name='tag'),
]

