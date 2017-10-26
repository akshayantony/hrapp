from django.conf.urls import url
from . import views

app_name='homepage'

urlpatterns=[
    url(r'^$',views.CandidateFormView.as_view(),name='cform'),
    url(r'^charge/$', views.ChargeView.as_view(), name="charge"),
]
