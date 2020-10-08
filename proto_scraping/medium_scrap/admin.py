from django.contrib import admin
from .models import SearchHistory,Tag,Article
# Register your models here.

admin.site.register(SearchHistory)
admin.site.register(Tag)
admin.site.register(Article)