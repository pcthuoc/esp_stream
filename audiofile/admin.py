from django.contrib import admin
from .models import Audio

@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('name_file', 'date_created')
    list_filter = ('date_created',)
    search_fields = ('name_file',)
