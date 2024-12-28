from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('createroom', views.createRoom, name="createroom"),
    path('updateroom/<str:pk>/', views.updateroom, name="updateroom"),
    path('deleteroom/<str:pk>/', views.deleteroom, name="deleteroom"),
    path('login/', views.loginpage, name="login"),
    path('logout/', views.logoutuser, name="logout"),
    path('register/', views.registeruser, name="register"),
    path('delete-message/<str:pk>/', views.deletemessage, name="delete-message"),
    path('profile/<str:pk>/', views.userprofile, name="profile"),
    path('edit-user/', views.edituser, name="edit-user"),
    path('topics/', views.topicspage, name="topics"),
    path('activity/', views.activitypage, name="activity"),
]