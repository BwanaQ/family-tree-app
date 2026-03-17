from django.contrib import admin
from .models import Person, FamilyUnion, ParentChild


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'gender', 'clan', 'tribe')
    search_fields = ('first_name', 'last_name', 'clan', 'tribe')


@admin.register(FamilyUnion)
class FamilyUnionAdmin(admin.ModelAdmin):
    list_display = ('id', 'union_type', 'created_at')
    filter_horizontal = ('partners',)


@admin.register(ParentChild)
class ParentChildAdmin(admin.ModelAdmin):
    list_display = ('parent', 'child')