from django.contrib import admin
from .models import KnownPerson, UnknownPerson,PersonSighting
from django.utils.html import format_html

@admin.register(KnownPerson)
class KnownPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'camera_name')
    readonly_fields = ('photo_tag',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:100px;"/>', obj.photo.url)
        return ""
    photo_tag.short_description = 'Photo Preview'


@admin.register(UnknownPerson)
class UnknownPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'camera_name')
    readonly_fields = ('photo_tag',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:100px;"/>', obj.photo.url)
        return ""
    photo_tag.short_description = 'Photo Preview'

@admin.register(PersonSighting)
class PersonSightingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_person_name', 'location', 'timestamp')
    list_filter = ('location', 'timestamp')
    search_fields = ('known_person__name', 'unknown_person__name', 'location')
    readonly_fields = ('timestamp',)

    def get_person_name(self, obj):
        if obj.known_person:
            return obj.known_person.name
        elif obj.unknown_person:
            return obj.unknown_person.name
        return "Unknown"
    get_person_name.short_description = 'Person'