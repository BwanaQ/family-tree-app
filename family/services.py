# services.py
from collections import deque
from typing import List, Tuple, Dict

from django.db.models import Prefetch

from .models import Person, ParentChild, FamilyUnion  # adjust names if your models differ


# ---------- Graph helpers (DB queries) ----------

def get_parent_ids(person: Person) -> List[int]:
    """Return IDs of parents of `person`."""
    return list(
        ParentChild.objects.filter(child=person).values_list("parent", flat=True)
    )


def get_child_ids(person: Person) -> List[int]:
    """Return IDs of children of `person`."""
    return list(
        ParentChild.objects.filter(parent=person).values_list("child", flat=True)
    )


def get_spouse_ids(person: Person) -> List[int]:
    """Return IDs of spouses/partners for `person` via FamilyUnion.partners M2M."""
    spouse_ids = set()
    unions = FamilyUnion.objects.filter(partners=person).prefetch_related("partners")
    for u in unions:
        for partner in u.partners.all():
            if partner.pk != person.pk:
                spouse_ids.add(partner.pk)
    return list(spouse_ids)


def get_neighbors_with_meta(person: Person) -> List[Tuple[int, str, Dict]]:
    """
    Return neighbors for BFS: list of (neighbor_id, relation, meta).
    relation is one of: 'parent', 'child', 'spouse'
    meta is a dict; for spouse edges we include {'type': 'union'}.
    """
    neighbors = []
    for pid in get_parent_ids(person):
        neighbors.append((pid, "parent", {"type": "biological"}))
    for cid in get_child_ids(person):
        neighbors.append((cid, "child", {"type": "biological"}))
    for sid in get_spouse_ids(person):
        neighbors.append((sid, "spouse", {"type": "union"}))
    return neighbors


# ---------- Path analysis & interpretation ----------

def analyze_path(path: List[Tuple[str, Dict]]) -> Tuple[int, int, int, int]:
    """
    Given a path (list of (relation, meta)) from p1 -> ... -> p2,
    return (up, down, spouses, union_links).
    up = number of 'parent' steps (p moves up to ancestor)
    down = number of 'child' steps
    spouses = number of 'spouse' steps
    union_links = number of meta['type']=='union' steps
    """
    up = down = spouses = union_links = 0
    for relation, meta in path:
        if relation == "parent":
            up += 1
        elif relation == "child":
            down += 1
        elif relation == "spouse":
            spouses += 1
        if meta.get("type") == "union":
            union_links += 1
    return up, down, spouses, union_links


def _ordinal(n: int) -> str:
    """Simple ordinal helper for cousin degree labels."""
    ordinals = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth"}
    return ordinals.get(n, f"{n}th")


def interpret_relationship(path: List[Tuple[str, Dict]], p1: Person, p2: Person) -> str:
    """
    Interpret path (from p1 to p2) as a relationship label describing p1 relative to p2.
    Uses p1.gender ('M'/'F') to choose gendered labels.
    """
    up, down, spouses, union_links = analyze_path(path)
    g = getattr(p1, "gender", None)

    def gendered(male: str, female: str, other: str = None) -> str:
        if g == "M":
            return male
        if g == "F":
            return female
        return other or female

    # Prioritize in-law/spouse-aware patterns when any spouse edges are present
    if spouses > 0:
        # Parent-In-Law: p1 -> child -> ... -> p2  (down == 1, up == 0)
        if down == 1 and up == 0:
            return gendered("Father-In-Law", "Mother-In-Law")

        # Child-In-Law: p1 -> parent -> ... -> p2  (up == 1, down == 0)
        if up == 1 and down == 0:
            return gendered("Son-In-Law", "Daughter-In-Law")

        # For nephew/niece and uncle/aunt, prefer plain labels (no "-In-Law")
        if up == 2 and down == 1:
            return gendered("Nephew", "Niece")

        if up == 1 and down == 2:
            return gendered("Uncle", "Aunt")

        # Sibling-In-Law
        if up == 1 and down == 1:
            return gendered("Brother-In-Law", "Sister-In-Law")

        # Generic in-law fallback
        return "In-Law"

    # Non in-law (biological / step) relationships
    # Ancestor: p1 is ancestor of p2 (down > 0, up == 0)
    if up == 0 and down > 0:
        if down == 1:
            return gendered("Father", "Mother")
        if down == 2:
            return gendered("Grandfather", "Grandmother")
        if down == 3:
            return gendered("Great-Grandfather", "Great-Grandmother")
        return "Ancestor"

    # Descendant: p1 is descendant of p2 (up > 0, down == 0)
    if down == 0 and up > 0:
        if up == 1:
            return gendered("Son", "Daughter")
        if up == 2:
            return gendered("Grandson", "Granddaughter")
        if up == 3:
            return gendered("Great-Grandson", "Great-Granddaughter")
        return "Descendant"

    # Siblings
    if up == 1 and down == 1 and union_links == 0:
        return gendered("Brother", "Sister")
    if up == 1 and down == 1 and union_links > 0:
        return gendered("Step-Brother", "Step-Sister")

    # Uncle/Aunt and Nephew/Niece (biological)
    if up == 1 and down == 2:
        return gendered("Uncle", "Aunt")
    if up == 2 and down == 1:
        return gendered("Nephew", "Niece")

    # Grand-uncle / grand-nephew
    if up == 1 and down == 3:
        return gendered("Granduncle", "Grandaunt")
    if up == 3 and down == 1:
        return gendered("Grandnephew", "Grandniece")

    # Cousins: compute cousin degree and removals
    if up >= 2 and down >= 2:
        degree = min(up, down) - 1  # 1 -> first cousin
        removed = abs(up - down)

        # Special cultural mapping:
        # If this is first-cousin-once-removed, map to niece/nephew or aunt/uncle
        # depending on generation (up > down means p1 is younger -> Niece/Nephew).
        if degree == 1 and removed == 1:
            if up > down:
                # p1 is the younger generation relative to p2 -> niece/nephew
                return gendered("Nephew", "Niece")
            elif up < down:
                # p1 is the older generation relative to p2 -> uncle/aunt
                return gendered("Uncle", "Aunt")
            # if equal (shouldn't happen when removed==1), fall through

        # Fallback to explicit cousin wording for other cases
        if degree <= 0:
            return "Cousin"
        degree_label = f"{_ordinal(degree)} cousin"
        if removed == 0:
            return degree_label  # "First cousin"
        if removed == 1:
            return f"{degree_label} once removed"
        if removed == 2:
            return f"{degree_label} twice removed"
        return f"{degree_label} {removed} times removed"

    # Polygamy / co-spouse
    if spouses >= 2:
        return gendered("Co-Husband", "Co-Wife")

    if union_links > 0:
        return "Step Relative"

    return "Distant Relative"


# ---------- Public API: find_relationship ----------

def find_relationship(p1: Person, p2: Person, max_depth: int = 10) -> str:
    """
    Return a human-readable relationship label describing p1 relative to p2.
    Performs BFS to find the shortest path between p1 and p2 in the family graph.
    """
    if p1.pk == p2.pk:
        return "Same person"

    # Quick spouse check (direct)
    if p2.pk in get_spouse_ids(p1):
        return "Husband" if getattr(p1, "gender", None) == "M" else "Wife"

    visited = set()
    queue = deque()
    # store paths as list of (relation, meta) from p1 to current node (excluding starting node)
    queue.append((p1.pk, []))
    visited.add(p1.pk)

    while queue:
        current_id, path = queue.popleft()

        if len(path) > max_depth:
            continue

        if current_id == p2.pk:
            return interpret_relationship(path, p1, p2)

        try:
            current_person = Person.objects.get(pk=current_id)
        except Person.DoesNotExist:
            continue

        for neighbor_id, relation, meta in get_neighbors_with_meta(current_person):
            if neighbor_id in visited:
                continue
            visited.add(neighbor_id)
            queue.append((neighbor_id, path + [(relation, meta)]))

    return "No relation found"