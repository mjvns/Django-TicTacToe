from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path

from .views import welcome

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome, name='tictactoe_welcome'),
    path('player/', include('player.urls')),
    path('games/', include('gameplay.urls')),
]
