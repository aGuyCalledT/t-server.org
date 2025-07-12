from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'webapp'

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about-me/', TemplateView.as_view(template_name='about_me.html'), name='about_me'), # Hier korrigiert
    path('imprint/', TemplateView.as_view(template_name='imprint.html'), name='imprint'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms-of-service/', TemplateView.as_view(template_name='terms_of_service.html'), name='terms'),

    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success_view, name='contact_success'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/like/<int:movie_index>/', views.like_movie, name='like_movie'),
    path('wishlist/delete/<int:movie_index>/', views.delete_movie, name='delete_movie'),
]
