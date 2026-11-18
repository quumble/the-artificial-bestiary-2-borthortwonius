# Secondary analysis v0.3: record and audit closure

Closed 18 November 2026, before any label existed for the held-aside audit or
targeted responses. Investigator: Bo Chesterton. Written by Claude Opus 5.5.
Everything here is post hoc and exploratory. The original releases, scorers
and registered analyses are unchanged.

## What was done

| Step | Date (UTC) | Record |
|---|---|---|
| Proposal v0.1 for Studies A, B and C | 14 Nov | [proposal/](proposal/Bestiary_2_Secondary_Analysis_Proposal_for_Fable.docx) |
| Plan v0.3 approved and committed before new results | 14 Nov | [PLAN_v0.3.md](PLAN_v0.3.md), commit `275678f` |
| Audit sample selected and locked: 12 development, 64 state-stratified, 4 targeted, disjoint | 14 Nov, 21:22 | [AUDIT_SAMPLE_COMMITMENT.json](AUDIT_SAMPLE_COMMITMENT.json), commit `004e7b8` |
| Study B (response consistency), then Study A (information efficiency) | 14 Nov, 21:23 | [Reader-guide report](results/Bestiary_2_Secondary_Results_v0.3.md) ([original .docx](results/Bestiary_2_Secondary_Results_v0.3.docx)); [EXECUTION_STATUS.md](EXECUTION_STATUS.md) |
| Development round: all 12 coded and confirmed | 14 Nov, 22:43–22:48 | [Export](audit-development/Bestiary2_development_2026-11-14T22-48-50-911Z.json), [CSV copy](audit-development/Bestiary2_development_2026-11-14T22-48-53-839Z.csv), [packet](audit-development/Bestiary_2_Audit_Development_Packet.docx) |

The development export's SHA-256
(`25c93ef8eb916b3061c1964f437a474c8df452e2efc544c2507de4a95152f40a`) and the
packet document's (`de9f5aaf7a8b4f02e3994bd1a9a55065f1368fe4d892b92a2d7fcd205db3c4fb`)
match the hashes already cited by the context heuristic's fixtures and the
export itself. In the export, all 12 items were confirmed under working codebook
"v0.3 development", revision 1, with an empty memo. The codebook was never revised in the tool.

The reader-guide Markdown is a pandoc conversion of the .docx, added for reading
on GitHub. The .docx is the original.

## What was not done

- **The codebook was never locked.** The plan required locking it after the
  development round and before opening the audit.
- **The 64 audit and 4 targeted responses were never coded.** No labels exist
  for them. Their packets and the unblinding key are not in this repository or
  in the implementation package. The commitment file records only hashes, so
  overlap with later human passes cannot be checked.
- **Study C was never run.** It stayed deferred and was never opted into.
- **The implementation package is not here.** That is
  `Bestiary_2_Secondary_Analysis_v0.3.zip` (2,574,162 bytes, SHA-256
  `aef5fdab598266bf333556dca4a43a758c5e5e7ee890fc7a3ab6c22e20ef6a5b`), holding
  code, complete tables, figures and receipts. It can be added unchanged later,
  verified against that hash. Until then, the reader-guide report is the
  record of the A and B results.

## Why the audit is closed rather than completed

- **Its main purpose is covered elsewhere.** The audit was a human check on
  the registered Fable scorer's description, nonrecognition and unmarked
  description. The investigator's
  [84-item pass](../supplement/coding-heuristics/human-pass/) scored those
  registered outputs on the same constructs. The later
  [41-item core audit](../supplement/coding-heuristics/zoned-heuristic-v1-1/quick/RESULTS.md)
  covered the final coding instrument.
- **Its one new construct belongs in a new study.** That construct is
  contextual presentation: whether a description reads as licensed invention,
  a guess or a factual account. It should be built in from the start, with a
  codebook frozen before collection, not added to this corpus after the fact.
- **The plan's sequence was not followed.** The development round fed a
  measurement redesign (a 24-card boundary exercise) that became the context
  heuristic, not a locked codebook for this audit. That heuristic's fixtures
  state that the old human decisions were not carried into the redesign. The
  investigator has since read 125 corpus responses in later passes. Coding the
  64 + 4 now would not be the audit the plan described.

## What this means for A and B

Studies A and B stand as exploratory analyses of frozen surface features,
without the planned human audit. Their report already limits them that way:
no factual-accuracy, belief or welfare claims; no endpoint rankings; separate
generation-noise and word-resampling scales rather than a variance
decomposition. The development labels are working judgments for codebook
development, not validation. The 24-card boundary decisions were not exported
into this record. The context heuristic's provenance describes them as a
preliminary ledger, later superseded in conversation.
