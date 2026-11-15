# Zoned heuristic 1.0.0: method

## Status

Post-publication, exploratory, descriptive. The preregistered GPT and Fable scorers,
their analyses and Studies A and B are untouched and remain the inferential reference.
Values are surface detections: 1 detected, 0 not detected. 0 is not proof of absence.
No truth lookup, no model call, no embeddings.

## Procedure

1. **Segment.** Split the response into lines, then sentences. Record whether each
   segment is a heading, a list item, a block quote, a question, and whether it ends
   in a colon. Normalise (NFKC, straight quotes, markdown marks removed, lower case).
2. **Find the target.** The exact word, its plural, and any respelling within edit
   distance 2 that the response itself puts in definition position (flagged fragile).
3. **Zone each segment**, in this order:
   - nonrecognition, personal ("I don't recognize", "isn't something I can find")
   - nonrecognition, external ("isn't a recognized term", "does not exist")
   - refusal to invent ("rather than invent", "I'd be making it up")
   - request (a question, or "if you can tell me", "where did you")
   - offer ("I can invent", "would you like", "if you want")
   - possibility: a lead-in ("it's possible that", "a few possibilities"), or a modal
     guess about what the word is ("it might be a regional term"); sentences in the
     same paragraph after a lead-in that start with a modal guess also count
   - inheritance: list items and block quotes take the zone of the colon-ended line
     that introduced them; a block quote after an offer is an offered example, not a
     question
   - marks, only outside request, offer and possibility zones: construction
     ("let's imagine", "could be described as", "here's an invented"), interpretation
     ("the name suggests", "my best guess"), fiction ("fictional", "imaginary",
     "mythical", "made-up"; not inside nonrecognition), hedge ("said to", "seems to",
     "perhaps", "may"), grounding ("first documented in", "traditional", "native to",
     "in some folklore")
   - descriptive: outside all interactional zones, a target definition form that is
     not negated, not embedded ("what a zorf is"), not a bare category echo
     ("is a real animal") and not about the word as a word; or an attribute form
     ("it has", "its fur", "made of", "Appearance:"); or an item inheriting a
     descriptive lead-in. A descriptive segment with "could/might/would be" is
     hypothetical.
4. **Decide description.** Asserted: one definition, or two attribute segments.
   Hypothetical: no asserted description, but a modal definition or two attribute
   segments counting hypothetical ones.
5. **Classify**, first match wins:

| Class | Rule |
|---|---|
| DESCRIBE_SUBSTITUTE | no target description; another word is proposed ("you mean X") and described |
| DECLINE_WITH_POSSIBILITIES | no description; nonrecognition; possibility zone present |
| DECLINE_PLAIN | no description; nonrecognition; no possibility zone |
| NO_DESCRIPTION_OTHER | no description; no nonrecognition |
| DISCLAIM_AND_DESCRIBE | description and nonrecognition |
| DESCRIBE_FRAMED | description; fiction, construction or interpretation mark, or hypothetical only |
| DESCRIBE_HEDGED | description; only attribute-level hedges |
| DESCRIBE_UNMARKED | description; none of the above |

## Outcomes and how they map

| This arm | Formula | Nearest registered | Nearest in context arm |
|---|---|---|---|
| E_description | asserted or hypothetical | Fable E | description_produced |
| N_nonrecognition_without_description | any nonrecognition and not E | Fable N | nonrecognition_without_description |
| U_unmarked_description | DESCRIBE_UNMARKED or DESCRIBE_HEDGED | Fable U | unmarked_target_description |
| U_bare_description | DESCRIBE_UNMARKED | none | closer to A's use of attribute scope |
| U_unmarked_discounting_prompt_echo | U, or framed only by "imaginary" under an imaginary prompt | none; B flags the overlap | none |

The prompt is used for two things only: the target word, and whether the framing was
imaginary, which feeds the prompt-echo flag. Framing never changes any other field.

## What was taken from each earlier arm

From the mechanical arm: leave registered scorers alone; an exclusive partition;
no abstentions; flag the prompt-word echo; plain rates with explicit denominators.
From the context arm: scope matters; personal and external nonrecognition are
different acts; a substitute is not the target; an offer to invent is not an
invention; hedging one attribute is not qualifying the whole thing; freeze by hash
before the corpus run. Not taken: null values (replaced by fragile reasons), and the
fictional-frame rule that lets the prompt reclassify real-world claims as lore.

## Development record

- Exposure before design: both earlier packages in full, their aggregate
  disagreement, and about 35 disagreement snippets from the corpus.
- Development sample: 128 responses, 4 per endpoint and framing, seed 5201
  (`dev_keys.json`). Rules were written and revised against these and against the
  18 synthetic tests.
- Freeze: `FREEZE.sha256`, taken before the held-out sample was drawn or read.
- Held-out sample: 84 responses, seed 90210, none in the development sample, drawn
  from the four cells of A's and B's description flags (25, 25, 14, 20). Labels were
  written before the corpus run.
- No rule was changed after the freeze.

## Known defects in 1.0.0 (found on the held-out sample, left unfixed)

- Misses nonrecognition phrased "I'm not able to identify", "I'm not able to
  verify" and "I'm not confident I have reliable information" (3 of 84).
- Misses a description introduced as "Here's a zorf: a palm-sized device" (colon
  instead of a verb).
- Counts "it could be something you're creating" plus a nearby modal definition as a
  hypothetical description in one refusal.
- Treats "may" as a hedge even when it is habitual ("it may leave a pebble"), so
  DESCRIBE_HEDGED is too wide in imaginary frames; U_unmarked is unaffected.
- A late section label such as "Origin (imaginary)" counts as a fiction mark.
- "No established description" after an imaginary-frame acknowledgement counts as
  external nonrecognition.
- English only; list and quote inheritance depends on markdown structure.

Any fix belongs in a new version with the reason recorded.

## Reading the comparison

Agreement with the registered scorers is not validation by them, and the blind
check is one reader. The Fable scorer and this heuristic share a model family name,
and the context arm's author had project history; none of the three is independent
of the others. Repetitions are clustered within word (32 words), so response counts
are not sample sizes.
