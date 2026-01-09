from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('medication/add/', views.add_medication, name='add_medication'),
    path('medication/<int:med_id>/schedule/add/', views.add_schedule, name='add_schedule'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/taken/', views.mark_taken, name='mark_taken'),
    path('notifications/<int:pk>/missed/', views.mark_missed, name='mark_missed'),
    path("medication/delete/<int:med_id>/", views.delete_medication, name="delete_medication"),
    path("schedule/delete/<int:schedule_id>/", views.delete_schedule, name="delete_schedule"),
]