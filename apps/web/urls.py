from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    # Menu
    path("menu/", views.menu, name="menu"),
    path("menu/<slug:slug>/", views.coffee_detail, name="coffee"),
    # Building the order
    path("order/start/", views.order_start, name="order_start"),
    path("order/milk/", views.order_milk, name="order_milk"),
    path("order/size/", views.order_size, name="order_size"),
    path("order/review/", views.order_review, name="order_review"),
    # Paying and picking up
    path("order/<str:number>/pay/", views.order_pay, name="order_pay"),
    path("order/<str:number>/preparing/", views.order_preparing, name="order_preparing"),
    path("order/<str:number>/ready/", views.order_ready, name="order_ready"),
]
