from rest_framework.permissions import BasePermission
from .models import TreeContributor


class IsTreeMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(obj, 'tree'):
            tree = obj.tree
        else:
            return False

        if tree.owner == user:
            return True

        return TreeContributor.objects.filter(
            tree=tree,
            user=user
        ).exists()
