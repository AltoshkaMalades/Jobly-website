from django.contrib import admin
from .models import Job
from .models import Favorite

admin.site.register(Favorite)

admin.site.register(Job)