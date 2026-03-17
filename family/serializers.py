from rest_framework import serializers
from .models import Person, FamilyUnion, ParentChild


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class FamilyUnionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyUnion
        fields = '__all__'


class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = '__all__'