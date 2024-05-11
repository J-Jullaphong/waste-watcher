from django.urls import path
from django.views.generic import TemplateView
from .views import *
from .api_views import *

app_name = "waste"

urlpatterns = [
    path("", TemplateView.as_view(template_name="homepage.html"), name="home"),
    path("latest/", LatestWasteView.as_view(), name="latest"),
    path("comparison/", WasteLevelComparisonView.as_view(), name="comparison"),

    path('api/', TemplateView.as_view(template_name="swagger.html"), name="swagger"),
    path('api/bins/', ListBinsAPI.as_view()),
    path('api/bins/<int:pk>/', SpecificBinAPI.as_view()),
    path('api/waste/latest/', ListLatestWastesAPI.as_view()),
    path('api/waste/latest/bin/<int:bin>/', SpecificLatestWasteAPI.as_view()),
    path('api/waste/latest/location/<str:location>/', SpecificLatestWasteAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/<int:day>/', ListPeriodWastesAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/<int:day>/bin/<int:bin>/', SpecificPeriodWasteAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/<int:day>/location/<str:location>/', SpecificPeriodWasteAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/', ListPeriodWastesAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/bin/<int:bin>/', SpecificPeriodWasteAPI.as_view()),
    path('api/waste/<int:year>/<int:month>/location/<str:location>/', SpecificPeriodWasteAPI.as_view()),
    path('api/waste/<int:year>/', ListPeriodWastesAPI.as_view()),
    path('api/waste/<int:year>/bin/<int:bin>/', SpecificPeriodWasteAPI.as_view()),
    path('api/waste/<int:year>/location/<str:location>/', SpecificPeriodWasteAPI.as_view()),

    path('<path:undefined_path>/', UnavailableView.as_view(), name="404"),
]

