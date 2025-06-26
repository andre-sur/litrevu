"""
URL configuration for mon_projet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from myapp import views
from django.views.generic import TemplateView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),  
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # Vue de connexion
    path('flux/', views.user_feed, name='user_feed'),
    path('deconnexion/', views.deconnexion_view, name='logout'),
    path('follow/', views.follow_user_view, name='follow_user'),
    path('manage_follows/', views.manage_follows, name='manage_follows'),
    path('reviews/add/<int:ticket_id>/', views.create_review, name='create_review'),
    path('edit_ticket/<int:ticket_id>/', views.edit_ticket, name='edit_ticket'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    #path('create_review/', views.create_review, name='create_review'),
    #path('edit_review/', views.edit_review, name='edit_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('confirm_delete_review/<int:review_id>/', views.confirm_delete_review, name='confirm_delete_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    path('confirm_delete_ticket/<int:ticket_id>/', views.confirm_delete_ticket, name='confirm_delete_ticket'),
    path('delete_ticket/<int:review_id>/', views.delete_ticket, name='delete_ticket'),


    path('ticket_selection/', views.ticket_selection, name='ticket_selection'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    #path('add_review/<int:ticket_id>/', views.add_review, name='add_review'),
    #path('reviews/<int:ticket_id>/', views.ticket_reviews, name='ticket_reviews'),
    path('all_tickets/', views.all_tickets_view, name='all_tickets'),
    path('block_user/<int:user_id>/', views.block_user_view, name='block_user'),
    path('confirm_block_user/<int:user_id>/', views.confirm_block_user_view, name='confirm_block_user'),

   
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
