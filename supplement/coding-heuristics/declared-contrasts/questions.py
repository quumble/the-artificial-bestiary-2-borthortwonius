"""Explicit specifications for the eight declared Block 2 questions.

This module does not read the corpus or estimate any result. Every rate and
contrast is specified here so that the same list can be rerun on a later
instrument. Rates are fractions; differences are differences of fractions.
The estimator, including the common word bootstrap, is provided separately.
"""
from __future__ import annotations

from copy import deepcopy


ANTHROPIC = [
    "claude-sonnet-4-6", "claude-haiku-4-5",
    "claude-sonnet-5-5", "claude-haiku-5-5",
]
OPENAI = ["gpt-5.4-mini", "gpt-5.4-nano", "gpt-6-sol", "gpt-6-luna"]
HISTORICAL = ["claude-sonnet-4-6", "claude-haiku-4-5", "gpt-5.4-mini", "gpt-5.4-nano"]
CURRENT = ["claude-sonnet-5-5", "claude-haiku-5-5", "gpt-6-sol", "gpt-6-luna"]
MODELS = ANTHROPIC + OPENAI
CATEGORIES = ["animal", "object", "idea"]
REAL = ["real_" + category for category in CATEGORIES]
TYPE = ["type_of_" + category for category in CATEGORIES]
IMAGINARY = ["imaginary_" + category for category in CATEGORIES]
REAL_TYPE = REAL + TYPE
NONIMAGINARY = ["neutral"] + REAL_TYPE
ALL_CONDITIONS = NONIMAGINARY + IMAGINARY


def selection(field, conditions, *, arm="C", bank="fresh", models=None,
              denominator=None, statistic="mean"):
    """A named cell selection, with no implicit frame weighting."""
    result = {
        "arm": arm,
        "field": field,
        "bank": bank,
        "models": list(MODELS if models is None else models),
        "conditions": list(conditions),
        "statistic": statistic,
    }
    if denominator is not None:
        result["denominator"] = denominator
    return result


def _spec(question, suffix, label, terms, *, kind="contrast", **metadata):
    return {
        "id": f"Q{question}.{suffix}",
        "label": label,
        "block": 2,
        "tier": "secondary" if question in (3, 5, 8) else "primary",
        "terms": [{"coefficient": coefficient, "selection": deepcopy(value)}
                  for coefficient, value in terms],
        "metadata": {"question": question, "kind": kind, **metadata},
    }


def _rate(question, suffix, label, value, **metadata):
    return _spec(question, suffix, label, [(1.0, value)], kind="rate", **metadata)


def _difference(question, suffix, label, positive, negative, **metadata):
    return _spec(question, suffix, label,
                 [(1.0, positive), (-1.0, negative)], **metadata)


def build_questions():
    """Return the full, deterministic list of 159 Block 2 reporting rows.

    Endpoint base rates supporting a declared contrast are included as
    components. No between-endpoint ranking tests or additional populations
    are introduced. In particular, Q4's imaginary reference is pooled, Q3's
    four composition shares are pooled, and Q8's non-imaginary selection
    includes neutral alongside the six real and type-of conditions.
    """
    specs = []

    # Q1: conditional possibility-list share, seven conditions equally.
    def possibilities(models):
        return selection("type:DECLINE_WITH_POSSIBILITIES", NONIMAGINARY,
                         models=models, denominator="decline")

    for model in MODELS:
        specs.append(_rate(1, f"possibility_share.{model}",
                           f"Possibility-list share among declines: {model}",
                           possibilities([model]), model=model))
    specs.extend([
        _difference(1, "possibility_share.Anthropic_minus_OpenAI",
                    "Possibility-list share among declines: Anthropic minus OpenAI",
                    possibilities(ANTHROPIC), possibilities(OPENAI)),
        _difference(1, "possibility_share.current_minus_historical",
                    "Possibility-list share among declines: current minus historical",
                    possibilities(CURRENT), possibilities(HISTORICAL)),
    ])

    # Q2: endpoint real/type-of components, endpoint and pooled frame gaps,
    # and the generation gap over the six real and type-of conditions.
    def describe_anyway(conditions, models=None):
        return selection("type:DISCLAIM_AND_DESCRIBE", conditions, models=models)

    for model in MODELS:
        for frame, conditions in (("real", REAL), ("type_of", TYPE)):
            specs.append(_rate(2, f"describe_anyway.{frame}.{model}",
                               f"Disclaim and describe rate: {frame}, {model}",
                               describe_anyway(conditions, [model]),
                               model=model, framing=frame))
        specs.append(_difference(
            2, f"describe_anyway.type_of_minus_real.{model}",
            f"Disclaim and describe: type-of minus real, {model}",
            describe_anyway(TYPE, [model]), describe_anyway(REAL, [model]),
            model=model))
    specs.extend([
        _difference(2, "describe_anyway.type_of_minus_real.all",
                    "Disclaim and describe: type-of minus real, all endpoints",
                    describe_anyway(TYPE), describe_anyway(REAL)),
        _difference(2, "describe_anyway.current_minus_historical",
                    "Disclaim and describe: current minus historical, real and type-of",
                    describe_anyway(REAL_TYPE, CURRENT),
                    describe_anyway(REAL_TYPE, HISTORICAL)),
    ])

    # Q3: the exclusive response-type partition among descriptions.
    description_classes = {
        "bare": "DESCRIBE_UNMARKED",
        "hedged": "DESCRIBE_HEDGED",
        "framed": "DESCRIBE_FRAMED",
        "disclaimed": "DISCLAIM_AND_DESCRIBE",
    }

    def description_share(response_class, models=None):
        return selection("type:" + response_class, REAL_TYPE,
                         models=models, denominator="E")

    for name, response_class in description_classes.items():
        specs.append(_rate(3, f"description_share.{name}",
                           f"Share of descriptions that are {name}: real and type-of",
                           description_share(response_class), component=name))
    bare = description_classes["bare"]
    specs.extend([
        _difference(3, "bare_share.Anthropic_minus_OpenAI",
                    "Bare share among descriptions: Anthropic minus OpenAI",
                    description_share(bare, ANTHROPIC), description_share(bare, OPENAI)),
        _difference(3, "bare_share.current_minus_historical",
                    "Bare share among descriptions: current minus historical",
                    description_share(bare, CURRENT), description_share(bare, HISTORICAL)),
    ])

    # Q4: grounding is counted only when a target description is present.
    def grounding(conditions, models=None):
        return selection("described_grounding", conditions,
                         models=models, denominator="E")

    for model in MODELS:
        specs.append(_rate(4, f"grounding_share.{model}",
                           f"Grounding share among descriptions: real and type-of, {model}",
                           grounding(REAL_TYPE, [model]), model=model))
    specs.extend([
        _difference(4, "grounding_share.Anthropic_minus_OpenAI",
                    "Grounding share among descriptions: Anthropic minus OpenAI",
                    grounding(REAL_TYPE, ANTHROPIC), grounding(REAL_TYPE, OPENAI)),
        _difference(4, "grounding_share.real_minus_type_of",
                    "Grounding share among descriptions: real minus type-of",
                    grounding(REAL), grounding(TYPE)),
        _spec(4, "grounding_share.imaginary_reference",
              "Grounding share among descriptions: pooled imaginary reference",
              [(1.0, grounding(IMAGINARY))], kind="reference"),
    ])

    # Q5: unconditional imaginary-frame U rates. The second rate discounts
    # the prompt's literal word 'imaginary' as the only detected frame mark.
    for model in MODELS:
        counted = selection("U", IMAGINARY, models=[model])
        discounted = selection("U_unmarked_discounting_prompt_echo", IMAGINARY,
                               models=[model])
        specs.extend([
            _rate(5, f"unmarked_echo.counted.{model}",
                  f"Unmarked description rate counting prompt echo: {model}",
                  counted, model=model, echo_handling="counted"),
            _rate(5, f"unmarked_echo.discounted.{model}",
                  f"Unmarked description rate discounting prompt echo: {model}",
                  discounted, model=model, echo_handling="discounted"),
            _difference(5, f"unmarked_echo.discounted_minus_counted.{model}",
                        f"Prompt-echo sensitivity: discounted minus counted, {model}",
                        discounted, counted, model=model),
        ])

    # Q6: compare categories within word, averaging two frames equally.
    for arm in ("B", "C"):
        for group, models in (("all", MODELS), ("Anthropic", ANTHROPIC), ("OpenAI", OPENAI)):
            animal = selection("E", ["real_animal", "type_of_animal"],
                               arm=arm, models=models)
            for category in ("idea", "object"):
                other = selection("E", ["real_" + category, "type_of_" + category],
                                  arm=arm, models=models)
                specs.append(_difference(
                    6, f"description.{category}_minus_animal.{group}.{arm}",
                    f"Description rate: {category} minus animal, {group}, arm {arm}",
                    other, animal, arm=arm, group=group, category=category))

    # Q7: first compute within-cell pair agreement; the common estimator
    # then averages conditions, endpoints and source-balanced words.
    for bank in ("fresh", "known"):
        for model in MODELS:
            for arm in ("A", "B", "C"):
                specs.append(_spec(
                    7, f"binary_consistency.{bank}.{model}.{arm}",
                    f"Description-call pair agreement: {bank}, {model}, arm {arm}",
                    [(1.0, selection("E", ALL_CONDITIONS, arm=arm, bank=bank,
                                     models=[model], statistic="pair_agreement"))],
                    kind="consistency", arm=arm, bank=bank, model=model,
                    agreement_field="E"))
            specs.append(_spec(
                7, f"response_type_consistency.{bank}.{model}.C",
                f"Response-type pair agreement: {bank}, {model}, arm C",
                [(1.0, selection("response_type", ALL_CONDITIONS, bank=bank,
                                 models=[model], statistic="pair_agreement"))],
                kind="consistency", arm="C", bank=bank, model=model,
                agreement_field="response_type"))

    # Q8: positions are the frozen detector's cue positions. Attribute
    # hedges and implicit hypothetical framing have no position in v1.
    def late_marking(conditions, models):
        return selection("described_late_mark", conditions, models=models,
                         denominator="described_mark")

    for frame, conditions in (("imaginary", IMAGINARY), ("nonimaginary", NONIMAGINARY)):
        for provider, models in (("Anthropic", ANTHROPIC), ("OpenAI", OPENAI)):
            specs.append(_rate(
                8, f"late_marking.{frame}.{provider}",
                f"Late-only share among descriptions with positioned marks: {frame}, {provider}",
                late_marking(conditions, models), framing=frame, provider=provider))
        specs.append(_difference(
            8, f"late_marking.{frame}.Anthropic_minus_OpenAI",
            f"Late-only marking share: Anthropic minus OpenAI, {frame}",
            late_marking(conditions, ANTHROPIC), late_marking(conditions, OPENAI),
            framing=frame))

    return specs
