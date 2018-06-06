from django.urls import path

import extractor.views

urlpatterns = [
    path('', extractor.views.upload, name='index'),
    path('<uuid:id>/', extractor.views.pdf, name='pdf'),
]
