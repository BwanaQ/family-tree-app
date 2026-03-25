from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Tree, Person, FamilyUnion, ParentChild
from .serializers import *
from .services import find_relationship
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permissions import IsTreeMember

class TreeViewSet(viewsets.ModelViewSet):
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer
    permission_classes = [IsAuthenticated, IsTreeMember]


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated, IsTreeMember]

    def get_queryset(self):
        user = self.request.user

        return Person.objects.filter(
            tree__contributors__user=user
        ) | Person.objects.filter(
            tree__owner=user
        )


class FamilyUnionViewSet(viewsets.ModelViewSet):
    queryset = FamilyUnion.objects.all()
    serializer_class = FamilyUnionSerializer
    permission_classes = [IsAuthenticated, IsTreeMember]


class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer
    permission_classes = [IsAuthenticated, IsTreeMember]


# class RelationshipView(APIView):
#     def get(self, request):
#         # p1_id = request.GET.get('p1')
#         # p2_id = request.GET.get('p2')
#         p1_id = 2

#         p2_id = 10

        
#         try:
#             p1 = Person.objects.get(id=p1_id)
#             p2 = Person.objects.get(id=p2_id)
#             if p1.tree != p2.tree:
#                 return Response({"error": "Different trees"}, status=400)
#         except Person.DoesNotExist:
#             return Response({"error": "Invalid person ID"}, status=404)

#         relationship = find_relationship(p1, p2)

#         return Response({
#             "person1": {
#                 "id": p1.id,
#                 "first_name": p1.first_name,
#                 "last_name": p1.last_name
#             },
#             "person2": {
#                 "id": p2.id,
#                 "first_name": p2.first_name,
#                 "last_name": p2.last_name
#             },
#             "relationship": relationship
#         })


class RelationshipView(APIView):
    """
    E2E validation with expected vs actual (minimal payload).
    """

    def get(self, request):

        test_cases = [
        (2, 10, "Grandfather"),
        (6, 10, "Granduncle"),
        (10, 2, "Grandson"),
        (10, 6, "Grandnephew"),
        (2, 6, "Brother"),
        (1, 4, "Brother"),           # corrected
        (5, 10, "Mother"),
        (8, 1, "First cousin"),
        (3, 10, "Grandmother"),
        (9, 8, "Mother"),
        (7, 3, "Mother-In-Law"),     # corrected
        (3, 7, "Daughter-In-Law"),   # corrected
        (1, 6, "Nephew"),            # corrected
        (1, 9, "Nephew"),
        (4, 8, "First cousin"),
        (10,11, "Second cousin"),
        (11,1, "Niece"),
        (1,11, "Uncle"),
        (2,11, "Granduncle"),
        (8,10,"Uncle"),
        (7,10,"Great-Grandmother")
        


    ]

        results = []

        for p1_id, p2_id, expected in test_cases:

            try:
                p1 = Person.objects.get(id=p1_id)
                p2 = Person.objects.get(id=p2_id)

                # Skip cross-tree (safety)
                if p1.tree_id != p2.tree_id:
                    actual = "Different trees"
                else:
                    actual = find_relationship(p1, p2)

            except Person.DoesNotExist:
                actual = "Invalid person ID"

            results.append({
                "input": f"{p1_id}-{p2_id}",
                "expected": expected,
                "actual": actual,
                "pass": expected == actual
            })

        # Optional summary
        total = len(results)
        passed = sum(1 for r in results if r["pass"])

        return Response({
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed
            },
            "results": results
        })