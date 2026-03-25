from django.db import models
from django.contrib.auth.models import User

class Tree(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_trees')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TreeContributor(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('contributor', 'Contributor'),
        ('viewer', 'Viewer'),
    )

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='contributors')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('tree', 'user')


class Person(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='persons', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    date_of_birth = models.DateField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    date_of_death = models.DateField(null=True, blank=True)

    photo = models.ImageField(upload_to='persons/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FamilyUnion(models.Model):
    UNION_TYPES = (
        ('customary', 'Customary'),
        ('civil', 'Civil'),
        ('religious', 'Religious'),
        ('informal', 'Informal'),
    )

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='unions',null=True, blank=True)
    partners = models.ManyToManyField(Person, related_name='unions')
    union_type = models.CharField(max_length=20, choices=UNION_TYPES)

    def __str__(self):
        return f"Union {self.id}"


class ParentChild(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='relationships',null=True, blank=True)
    parent = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='children_links')
    child = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='parent_links')

    class Meta:
        unique_together = ('parent', 'child')