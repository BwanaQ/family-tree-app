from rest_framework import serializers
from .models import Tree, Person, FamilyUnion, ParentChild


class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'


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