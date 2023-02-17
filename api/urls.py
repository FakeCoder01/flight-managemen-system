
from django.urls import path
from . import views
  
urlpatterns = [
    path('', views.ApiOverview, name='api_routes'),
    path('search/flights/', views.SearchFlight, name="search_flights"),
    path('search/airports/', views.AirportFillUp, name="airport_fill_up"),
]