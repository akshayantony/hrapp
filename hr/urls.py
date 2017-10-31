from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^',include('homepage.urls'),name='homepage'),
    url(r'^login/$', auth_views.login,{'template_name': 'homepage/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,{ 'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
]
