"""Predicate schema for the fact layer.

Single-valued predicates can hold only one current value per subject, so a new
value either corrects or contradicts the old one. Multi-valued predicates can
hold many values at once, so a new value is usually additive.
"""

SINGLE = "single"
MULTI = "multi"

PREDICATES = {
    "lives_in": SINGLE,
    "works_at": SINGLE,
    "job_title": SINGLE,
    "studies_at": SINGLE,
    "relationship_status": SINGLE,
    "partner": SINGLE,
    "age": SINGLE,
    "allergic_to": MULTI,
    "likes": MULTI,
    "dislikes": MULTI,
    "has_skill": MULTI,
    "has_pet": MULTI,
    "has_child": MULTI,
    "hobby": MULTI,
    "plans_to": MULTI,
}


def is_single_valued(predicate: str) -> bool:
    return PREDICATES.get(predicate) == SINGLE
