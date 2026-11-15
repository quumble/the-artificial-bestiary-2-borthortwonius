# Execution and limits

The frozen contextual heuristic processed all **16,000 responses** and all
**2,560 repeated-response cells**. Verification checked all **151,300 evidence
spans** against the exact original responses. All 42 regression test methods
passed. Original source archives, scorers and outputs were left intact.

**4,233 responses (26.5%) have at least one unresolved field.** This does not
mean the whole response is unusable: other fields retain their own detections.
Nor does it estimate total error: a pattern miss may still appear as 0.
The broad qualification flag is unresolved in 1,836 responses; whole-target
qualification is unresolved in 4,206. These overlaps must not be added together.

No rule was revised after this corpus run. No independent temporary-chat
artifact has been inspected. The frozen version and this execution remain the
comparison baseline even if later review finds defects.

The immediate next step is to retain the independent ZIP exactly as supplied,
compare definitions, freeze a crosswalk, then compare genuinely commensurable
labels and identify disagreements. This package does not send the investigator
back through thousands of manual coding decisions.
