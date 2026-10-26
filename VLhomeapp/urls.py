from django.urls import path
from . import views

urlpatterns = [
    path("", views.menu_list, name="menu_list"),
    path("taomlar/", views.dish_list, name="dish_list"),
    path("buyurtma/", views.order_create, name="order_create"),
    path("holat/", views.order_lookup, name="order_lookup"),
    path("holat/<int:pk>/", views.order_detail, name="order_detail"),
]