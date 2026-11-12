from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Post, Tag, UserBookmark, UserProfile

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(UserBookmark)