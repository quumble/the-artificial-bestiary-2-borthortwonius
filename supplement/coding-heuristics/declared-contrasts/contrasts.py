"""Block 1: frozen-instrument re-estimates in the declared comparison shapes."""
from copy import deepcopy
from itertools import combinations

from estimation import IMAGINARY, REAL, TYPE, PRESUP, NONIMAGINARY
from inputs import MODELS

FRESH = ["fresh-animal-intent", "fresh-no-intent-claude", "fresh-no-intent-gpt"]
KNOWN = ["known-animal-intent", "known-no-intent"]
H4_FRESH_WEIGHTS = {FRESH[0]: .5, FRESH[1]: .25, FRESH[2]: .25}


def group(index, value):
    return [m for m, attributes in MODELS.items() if attributes[index] == value]


def selection(arm, outcome, conditions, **kwargs):
    return dict(arm=arm, field=outcome, bank="fresh", conditions=list(conditions), **kwargs)


def term(coefficient, selected):
    return dict(coefficient=coefficient, selection=selected)


def _terms(shape, outcome, arm):
    def s(conditions, **kwargs):
        return selection(arm, outcome, conditions, **kwargs)
    if shape in ("G1", "G2"):
        return [term(1, s(IMAGINARY if shape == "G1" else TYPE)), term(-1, s(REAL))]
    if shape == "H2":
        return [term(1, s(TYPE, models=group(0, "OpenAI"))), term(-1, s(REAL, models=group(0, "OpenAI")))]
    if shape == "H3":
        return [term(1, s(PRESUP, sources=FRESH[:1])), term(-1, s(PRESUP, sources=FRESH[1:]))]
    if shape == "H4":
        terms = []
        for bank, coefficient in (("known", 1), ("fresh", -1)):
            for generation, sign in (("current", 1), ("historical", -1)):
                selected = s(NONIMAGINARY, models=group(1, generation))
                selected["bank"] = bank
                if bank == "fresh":
                    selected.update(sources=FRESH, source_weights=H4_FRESH_WEIGHTS)
                terms.append(term(coefficient * sign, selected))
        return terms
    if shape == "H5":
        return [term(1, s(PRESUP, models=group(1, "current"))), term(-1, s(PRESUP, models=group(1, "historical")))]
    if shape == "H6":
        return [term(source_sign * provider_sign, s(NONIMAGINARY, sources=[source], models=group(0, provider)))
                for source, source_sign in ((FRESH[1], 1), (FRESH[2], -1))
                for provider, provider_sign in (("Anthropic", 1), ("OpenAI", -1))]
    raise ValueError(shape)


def build_contrasts():
    shapes = [("G1", f) for f in ("E", "N", "U")] + [("G2", f) for f in ("E", "N", "U")]
    shapes += [("H2", "N"), ("H3", "U"), ("H4", "N"), ("H5", "U"), ("H6", "N")]
    descriptions = {
        "G1": "Imaginary minus real, all endpoints, fresh",
        "G2": "Type-of minus real, all endpoints, fresh",
        "H2": "Type-of minus real, OpenAI endpoints, fresh",
        "H3": "Animal-intent minus no-intent words, real and type-of, fresh",
        "H4": "Current-minus-historical gap, known minus fresh, equal intent weights",
        "H5": "Current minus historical endpoints, real and type-of, fresh",
        "H6": "Anthropic-minus-OpenAI gap, Claude-origin minus GPT-origin fresh words",
    }
    specifications = []
    for shape, outcome in shapes:
        family = []
        for arm in ("A", "B", "C"):
            spec = dict(id=f"{shape}.{outcome}.{arm}", label=descriptions[shape], block=1,
                        tier="secondary" if outcome == "U" else "primary", shape=shape, outcome=outcome,
                        arm=arm, terms=_terms(shape, outcome, arm))
            if (shape, outcome) == ("G1", "E"):
                spec["aliases"] = [f"H1.E.{arm}"]
            family.append(spec)
            specifications.append(spec)
        for left, right in combinations(family, 2):
            terms = deepcopy(left["terms"])
            for t in deepcopy(right["terms"]):
                t["coefficient"] *= -1
                terms.append(t)
            specifications.append(dict(id=f"{shape}.{outcome}.{left['arm']}-{right['arm']}",
                label=descriptions[shape] + f"; instrument {left['arm']} minus {right['arm']}",
                block=1, tier=left["tier"], shape=shape, outcome=outcome,
                comparison=f"{left['arm']}-{right['arm']}", terms=terms,
                support_note="Difference of each instrument's available-case estimator, with shared word draws."))
    return specifications
