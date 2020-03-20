"""firstsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import include, url
from django.contrib import admin
from infoblox import views


admin.autodiscover()

urlpatterns = [ 
	url(r'^admin/', admin.site.urls),
	url(r'^dtc' , views.dtc, name='dtc'),
	url(r'^main/' , views.main_lbdn, name='main_lbdn'),
	url(r'^infoblox/', views.infoblox, name='infoblox'),
	url(r'^pool/', views.pool, name="pool"),
    url(r'' , views.main_lbdn, name='main_lbdn'),
]

