from collections import deque
from django.db import transaction
from .models import Person, FamilyUnion, ParentChild


# ------------------------
# CREATION SERVICES
# ------------------------

def create_person(**data):
    return Person.objects.create(**data)


def create_union(partners, union_type='customary'):
    """
    partners: list of Person instances
    """
    if len(partners) < 2:
        raise ValueError("A union must have at least two partners.")

    with transaction.atomic():
        union = FamilyUnion.objects.create(union_type=union_type)
        union.partners.set(partners)

    return union


def add_child(parent, child):
    if parent == child:
        raise ValueError("A person cannot be their own parent.")

    return ParentChild.objects.get_or_create(parent=parent, child=child)


# ------------------------
# BASIC RETRIEVAL
# ------------------------

def get_parents(person):
    return Person.objects.filter(children__child=person)


def get_children(person):
    return Person.objects.filter(parents__parent=person)


def get_spouses(person):
    unions = person.unions.all()
    spouses = set()

    for union in unions:
        for partner in union.partners.all():
            if partner != person:
                spouses.add(partner)

    return list(spouses)


# ------------------------
# DERIVED RELATIONSHIPS
# ------------------------

def get_siblings(person):
    parents = get_parents(person)
    siblings = set()

    for parent in parents:
        children = get_children(parent)
        siblings.update(children)

    return list(siblings - {person})


def get_half_siblings(person):
    parents = set(get_parents(person))
    half_siblings = set()

    for parent in parents:
        children = set(get_children(parent))

        for child in children:
            if child == person:
                continue

            child_parents = set(get_parents(child))

            # shares at least one parent but not all
            if parents.intersection(child_parents) and parents != child_parents:
                half_siblings.add(child)

    return list(half_siblings)


def get_step_siblings(person):
    parents = get_parents(person)
    step_siblings = set()

    for parent in parents:
        spouses = get_spouses(parent)

        for spouse in spouses:
            if spouse not in parents:
                children = get_children(spouse)
                step_siblings.update(children)

    return list(step_siblings - {person})


# ------------------------
# ADVANCED UTILITIES
# ------------------------

def get_ancestors(person, depth=10):
    ancestors = set()
    current_level = {person}

    for _ in range(depth):
        next_level = set()

        for p in current_level:
            parents = get_parents(p)
            next_level.update(parents)

        ancestors.update(next_level)
        current_level = next_level

    return ancestors


def find_common_ancestor(p1, p2):
    ancestors1 = get_ancestors(p1)
    ancestors2 = get_ancestors(p2)

    return ancestors1.intersection(ancestors2)


# ------------------------
# GRAPH ENGINE (BFS)
# ------------------------

def get_neighbors(person):
    neighbors = []

    # parents (up)
    for parent in get_parents(person):
        neighbors.append((parent, 'parent'))

    # children (down)
    for child in get_children(person):
        neighbors.append((child, 'child'))

    # spouses (side)
    for spouse in get_spouses(person):
        neighbors.append((spouse, 'spouse'))

    return neighbors


def find_relationship_path(start, end):
    visited = set()
    queue = deque([(start, [])])

    while queue:
        current, path = queue.popleft()

        if current == end:
            return path

        visited.add(current)

        for neighbor, relation in get_neighbors(current):
            if neighbor not in visited:
                queue.append((
                    neighbor,
                    path + [(current, relation, neighbor)]
                ))

    return None


# ------------------------
# PATH INTERPRETATION
# ------------------------

def simplify_path(path):
    directions = []

    for _, relation, _ in path:
        if relation == 'parent':
            directions.append('up')
        elif relation == 'child':
            directions.append('down')
        elif relation == 'spouse':
            directions.append('side')

    return directions


def ordinal(n):
    if n == 1:
        return "First"
    elif n == 2:
        return "Second"
    elif n == 3:
        return "Third"
    else:
        return f"{n}th"


def interpret_relationship(path):
    directions = simplify_path(path)

    up = directions.count('up')
    down = directions.count('down')
    side = directions.count('side')

    # ------------------------
    # Direct lineage
    # ------------------------
    if up > 0 and down == 0:
        if up == 1:
            return "Parent"
        elif up == 2:
            return "Grandparent"
        else:
            return f"{'Great-' * (up - 2)}Grandparent"

    if down > 0 and up == 0:
        if down == 1:
            return "Child"
        elif down == 2:
            return "Grandchild"
        else:
            return f"{'Great-' * (down - 2)}Grandchild"

    # ------------------------
    # Siblings
    # ------------------------
    if up == 1 and down == 1:
        return "Sibling"

    # ------------------------
    # Uncle / Aunt
    # ------------------------
    if up == 2 and down == 1:
        return "Uncle/Aunt"

    if up >= 3 and down == 1:
        return f"{'Great-' * (up - 2)}Uncle/Aunt"

    # ------------------------
    # Cousins
    # ------------------------
    if up >= 1 and down >= 1:
        cousin_level = min(up, down) - 1
        removal = abs(up - down)

        if cousin_level >= 1:
            if removal == 0:
                return f"{ordinal(cousin_level)} Cousin"
            else:
                return f"{ordinal(cousin_level)} Cousin {removal} times removed"

    # fallback
    return "Extended Relative"


# ------------------------
# PUBLIC RELATIONSHIP FUNCTION
# ------------------------

def find_relationship(p1, p2):
    if p1 == p2:
        return "Same person"

    path = find_relationship_path(p1, p2)

    if not path:
        return "No relation found"

    return interpret_relationship(path)