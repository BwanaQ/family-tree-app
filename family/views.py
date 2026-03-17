from rest_framework import viewsets
from .models import Person, FamilyUnion, ParentChild
from .serializers import PersonSerializer, FamilyUnionSerializer, ParentChildSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class FamilyUnionViewSet(viewsets.ModelViewSet):
    queryset = FamilyUnion.objects.all()
    serializer_class = FamilyUnionSerializer


class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer