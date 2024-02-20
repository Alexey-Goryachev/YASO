from django.contrib import admin

from .models import NetModels, Labels

# Register your models here.

admin.site.register(NetModels)
admin.site.register(Labels)
