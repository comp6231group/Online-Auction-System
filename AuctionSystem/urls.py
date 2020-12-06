"""AuctionSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from pages.views import login_view, home_view, register_view, upload_product_view, product_view, products_list_view, purchases_view, login_view, deregister_view

urlpatterns = [
	path('', login_view, name="login-view"),
    path('registeruser/', register_view, name="register-view"),
    path('home/', home_view, name='home-view'),
    path('home/uploadproduct/', upload_product_view, name="upload-product-view"),
    path('viewproduct/<int:productid>', product_view, name='product-view'),
    path('home/productslist/', products_list_view, name='products-list-view'),
    path('home/viewpurchases/', purchases_view, name='purchases-view'),
    path('viewproduct/', product_view, name='product-view'),
    path('logout/', login_view, name='logout-view'),
    path('deregister/', deregister_view, name='deregister-view'),
    path('admin/', admin.site.urls),
]
