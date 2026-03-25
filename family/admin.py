from django.contrib import admin
from .models import Tree, TreeContributor, Person, FamilyUnion, ParentChild


# ------------------------
# Tree Admin
# ------------------------
@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('created_at',)


# ------------------------
# Tree Contributor Admin
# ------------------------
@admin.register(TreeContributor)
class TreeContributorAdmin(admin.ModelAdmin):
    list_display = ('id', 'tree', 'user', 'role')
    list_filter = ('role', 'tree')
    search_fields = ('user__username', 'tree__name')


# ------------------------
# Person Admin
# ------------------------
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'gender',
        'tree',
        'is_alive',
        'date_of_birth',
        'date_of_death'
    )
    list_filter = ('gender', 'is_alive', 'tree')
    search_fields = ('first_name', 'last_name')
    autocomplete_fields = ('tree', 'created_by')


# ------------------------
# Family Union Admin
# ------------------------
@admin.register(FamilyUnion)
class FamilyUnionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tree', 'union_type')
    list_filter = ('union_type', 'tree')
    filter_horizontal = ('partners',)  # 👈 nice UI for many-to-many


# ------------------------
# Parent-Child Admin
# ------------------------
@admin.register(ParentChild)
class ParentChildAdmin(admin.ModelAdmin):
    list_display = ('id', 'tree', 'parent', 'child')
    search_fields = ('parent__first_name', 'child__first_name')
    list_filter = ('tree',)