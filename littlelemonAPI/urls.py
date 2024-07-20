from django.contrib import admin
from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('users/token/login/',obtain_auth_token),
    
    path('users/',views.users),
    path('users/me/',views.get_user_data),
    path('menu-items/',views.menuitems),
    path('menu-item/<int:pk>',views.menuitem),
    path('groups/manager/users/',views.managercontrol),
    path('menu-items/cart/',views.Cart),
    path('orders/',views.orders),
    path('orders/<int:pk>',views.Order),
    path('groups/manager/users/<int:pk>',views.managercontrol),
    path('groups/delvcrew/users/<int:pk>',views.delv_crew_control),
    
    
    
]
