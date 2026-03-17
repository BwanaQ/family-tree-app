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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Relationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
    ]

    from_person = models.ForeignKey(Person, related_name='from_person', on_delete=models.CASCADE)
    to_person = models.ForeignKey(Person, related_name='to_person', on_delete=models.CASCADE)
    relationship_type = models.CharField(max_length=10, choices=RELATIONSHIP_TYPES)

    def __str__(self):
        return f"{self.from_person} → {self.relationship_type} → {self.to_person}"