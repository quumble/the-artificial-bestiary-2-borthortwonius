# Crosswalk frozen before any agreement was computed (2026-11-15)
A = Bestiary_2_Context_Heuristic_v1 (results/response_codes.jsonl); B = bestiary2_coding_heuristic run on analysis/response-features.jsonl.
Join key: (batch, model_requested, trial_id). A nulls excluded from agreement, coverage reported.
Tier 1 - same named construct by design
 1 description_produced              <-> F_E
 2 nonrecognition_without_description <-> F_N
 3 unmarked_target_description       <-> F_U
 4 knowledge_limit                   <-> F_nonrec
Tier 2 - overlapping constructs, definitional gap expected
 5 target_description                <-> M09
 6 target_description                <-> F_E
 7 knowledge_limit                   <-> M03
 8 construction_acknowledgment       <-> F_construct OR F_interp
 9 qualifier_anywhere                <-> F_cue_any
10 qualifier_anywhere                <-> F_cue_any OR M02 OR S_OFFER OR S_CONTEXT_REQUEST
11 target_qualification              <-> M02
12 external_negative                 <-> F_nonrec (containment only)
13 substitute_description            <-> S_WORD_REPAIR (containment only)
14 scope:separate_offer_request      <-> S_OFFER OR S_CONTEXT_REQUEST
15 B response_class collapsed to {desc+nonrec, desc no nonrec, nonrec no desc, neither} <-> A (description_produced, knowledge_limit)
Unmatched A: category_mismatch, premise_retention, implicit_existence, explicit_existence, real_world_grounding, pb_worldbuilding, mixed_status, target_unqualified_description
Unmatched B: M01/S_FICTION, S_NEGATED_DEFINITION, quote/local-negation flags, S_PROMPT_IMAGINARY_OVERLAP, S_CATEGORY_WORDS, eligibility columns
