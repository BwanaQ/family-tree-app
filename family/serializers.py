from rest_framework import serializers
from .models import Person, Relationship

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'