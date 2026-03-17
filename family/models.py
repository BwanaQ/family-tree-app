from django.db import models


class Person(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    # Extra fields
    is_alive = models.BooleanField(default=True)
    date_of_death = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='person_photos/', null=True, blank=True)
    
    # Optional African context fields
    clan = models.CharField(max_length=100, blank=True)
    tribe = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class FamilyUnion(models.Model):
    """
    Represents a marriage or partnership.
    Supports polygamy naturally.
    """

    UNION_TYPES = [
        ('customary', 'Customary Marriage'),
        ('civil', 'Civil Marriage'),
        ('religious', 'Religious Marriage'),
        ('informal', 'Informal Union'),
    ]

    partners = models.ManyToManyField(Person, related_name='unions')
    union_type = models.CharField(max_length=20, choices=UNION_TYPES, default='customary')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        partner_names = ", ".join([str(p) for p in self.partners.all()])
        return f"Union: {partner_names}"


class ParentChild(models.Model):
    parent = models.ForeignKey(Person, related_name='children', on_delete=models.CASCADE)
    child = models.ForeignKey(Person, related_name='parents', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return f"{self.parent} → parent → {self.child}"