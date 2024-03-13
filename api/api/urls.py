"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
import json
from django.urls import path
from django.http import JsonResponse
from . import ai

def action(request):
    body_unicode = request.body.decode('utf-8')
    req_body = json.loads(body_unicode)

    output = ai.process(req_body['message'])
    
    return JsonResponse(data={'data': output})

urlpatterns = [
    path('completions', action)
]
