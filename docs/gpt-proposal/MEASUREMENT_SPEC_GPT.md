# Bestiary 2: deterministic measurement specification

Version: `gpt-bestiary-2-v1.0`. Prepared November 10, 2026, America/New_York.

This specification and `inventories-gpt-v1.json` are normative appendices to `PREREGISTRATION_GPT.md`. They specify all 32 proposed families without claiming that software has already implemented or validated them. Implement and pass the fixture requirements before collecting study responses. If implementation requires a substantive change, version and disclose it before collection.

## Common text contract

1. Preserve the exact provider payload and extracted visible text. Score only assistant-visible text, including text carried by a structured refusal. Exclude prompts, metadata, hidden reasoning, and tool content. Join separate visible blocks in provider order with one newline. Keep block boundaries and the original block strings, so join characters are distinguishable from generated characters.
2. For the matching view, transform each raw Unicode code point separately using Python `unicodedata.normalize('NFKC', ch).casefold()`. This is deliberately characterwise normalization, not full-string recomposition. Map U+2018, U+2019 and U+02BC to ASCII apostrophe and CRLF/CR to LF. Keep, for each transformed character, its originating half-open raw character span. Casefold expansions inherit the same raw span. Raw characters mean Python Unicode code points, not bytes or UTF-16 units.
3. Segment at each LF and immediately after a run of `.`, `?`, or `!` followed by whitespace or end of text. Discard empty segments. A decimal point inside `1.5` is not a boundary. This intentionally treats headings and list lines as sentence-like segments. It is not a grammatical sentence parser.
4. Within segments, tokenize the transformed text using Python Unicode regex `[^\W\d_]+(?:'[^\W\d_]+)*|\d+(?:[.,]\d+)*`. Thus contractions remain one token, hyphens split tokens, numbers count as words, and Markdown punctuation does not count as a word. No stemming, spell correction, lemmatization, stop-word removal, or synonym expansion unless explicitly stated below. Preserve token character spans and segment membership. All references to words below mean these tokens.
5. Match inventory phrases as exact contiguous token sequences within a single segment, with arbitrary intervening non-token punctuation ignored. Tokenize inventories by the same rule. Consequently `made-up` and `made up` match the same entry; `could` does not match `couldn't`. A phrase cannot bridge a segment boundary. A quote, a question or a negation never cancels a match.
6. Within each family, identify all candidates, order by ascending token start, then descending token length, then lexical entry string, and greedily keep non-overlapping token spans. Apply this separately to each explicitly named subfamily. For the family total, apply the same rule to the union of candidates rather than adding overlapping subfamily counts. Matches may overlap across families. M09 uses the same selection rule for competing suffixes.
7. For each retained match, save family, subfamily, inventory entry, token start and exclusive end, normalized span, raw span, raw matched text, and segment index. Store both occurrence count and any-match. Density is `100 * count / W`, where W is response token count. W=0 gives null density. Missing text gives null behavioral features, not zero. A usable response with no matches gives count 0 and any-match 0.
8. For each lexical or syntax match record `local_negation`: any token from `no, not, never, neither, nor, without, isn't, aren't, wasn't, weren't, don't, doesn't, didn't, can't, cannot, couldn't, won't, wouldn't` among the three preceding tokens or inside the match, restricted to its segment. This is a proximity flag only.
9. Record mechanical quotation overlap using paired raw ASCII double quotes, paired U+201C/U+201D double quotes, and paired single backticks, independently within each raw line. Pair successive straight delimiters, or pair each left curly delimiter with the next right one. Unmatched delimiters create no span. Do not parse single-quoted passages, Markdown fences or nesting. A match is quote-overlapping if its raw span intersects an enclosed span. Preserve the flag without changing the primary count.
10. `C` is the union of M01, M02, M03 and M04 retained match spans. It is a cue inventory union, not a semantic qualification label. Other families never enter C. Raw Markdown is retained. No Markdown-to-HTML parser or language detector is used. Non-English responses remain eligible but lexicon coverage is limited to the fixed English inventories.

## Exact family definitions

All lexical entries below refer to the JSON appendix. Only listed forms are included. For each lexical family retain entry-level counts in addition to family totals.

| ID | Frozen operation and outputs |
| --- | --- |
| M01 | Fiction-expression matching using M01. Any-match is a primary outcome. |
| M02 | Qualification-expression matching using M02, with modal and hedge components. Union any-match is a primary outcome. |
| M03 | Non-recognition-expression matching using M03. Any-match is a primary outcome. The intentionally narrow list includes some formulations that can refer to something other than the target. |
| M04 | Construction-expression matching using M04. Counts, any-match and density are secondary. |
| M05 | Interpretation-expression matching using M05. |
| M06 | Realness and certainty expressions, separately using M06 subfamilies. No combined confidence score. |
| M07 | Context-request expressions using M07. |
| M08 | Help/co-creation expressions using M08. |
| M09 | Exact normalized target token immediately followed by any token sequence in M09_suffixes within its segment. Article before the target is immaterial and not part of the match. No pluralization or possessive matching. Includes `target is not`, and Markdown-decorated targets. Any-match is a primary outcome. |
| M10 | Attribute-statement forms using M10. These are literal constructions without pronoun-reference resolution. |
| M11 | For each M01–M04 and their union C, record first match's raw character offset, zero-based word index j, and `j/W`. No match gives null for all positions and `no_match_observed=1`. A match on the first word has position 0. |
| M12 | For each M01–M04 and C, any-match in first and last nonempty segments, and first and last `ceil(0.20*W)` words. A window contains a match if the match's starting token lies in it. Windows may overlap. Empty text gives null. |
| M13 | Compare earliest M09 start with earliest C start: `definition_first`, `cue_first`, `tie`, `definition_only`, `cue_only`, or `neither`. Also report binary `definition_before_any_observed_cue`, true only for `definition_first` and `definition_only`. It describes order, not assertion of reality. |
| M14 | Count segments with M09 or M10 and no C match. Report fraction of all segments, and fraction of M09/M10-containing segments. A zero descriptive-segment denominator gives null. |
| M15 | Count segments with M09 or M10 and a C match. Report the same two fractions as M14 and separate M01–M04 co-occurrence counts. M14+M15 equals the number of M09/M10 segments. |
| M16 | Save each segment's binary vector `(M09,M10,M01,M02,M03,M04)`. For each of these six indicators, count adjacent `00,01,10,11` transitions and maximum consecutive 0 and 1 runs. With one segment transition counts are zero; a never-observed run has length zero. No extra inferred stance categories. |
| M17 | Number of raw characters and W. Report response-level values and medians/IQRs by cell as descriptive metadata. API token counts stay separate. |
| M18 | Nonempty segment count S, `W/S`, and largest segment word count. When S=0 the latter two are null. Segments containing only punctuation can have 0 words. |
| M19 | On raw lines, count headings matching `^ {0,3}#{1,6}\s+\S`, unordered list items matching `^\s*[-+*]\s+\S`, ordered list items matching `^\s*\d+[.)]\s+\S`, and paragraphs as nonblank line blocks separated by at least one blank line. Fenced-code content is not specially excluded. |
| M20 | Count literal raw ASCII `?` characters and retain raw positions. Fullwidth question marks are not counted in this raw-character measure. |
| M21 | First- and second-person reference matching using M21. Count a listed contraction once; never also count its substring pronoun. Includes `let's` in first person. |
| M22 | Count exact normalized target tokens. Separately let P be the set of prompt tokens excluding the target and M22_function_words, and R the set of response tokens. Prompt-content overlap is `|P intersect R|/|P|`, null if P is empty. It is coverage of the prompt vocabulary, not Jaccard. Neutral prompts have null overlap. |
| M23 | Count numeric tokens matching `\d+(?:[.,]\d+)*`, listed number words, and number-plus-unit pairs whose consecutive tokens are a numeric token or listed number word followed by one M23_units entry. All three counts are separate; overlap is allowed across them. Numeric list labels are included. |
| M24 | On normalized character text, count non-overlapping URL spans matching `https?://[^\s<>]+` and DOI spans matching `\b10\.\d{4,9}/[^\s<>]+`. Overlap across types is retained. Trim terminal `. , ; : ! ? ) ] }` from the stored URL/DOI span. Count parenthesized author/year forms matching `\([a-z]+(?: et al\.)?,?\s+(?:19|20)\d{2}[a-z]?\)` separately, plus M24_attribution phrases. These narrow patterns do not verify sources. |
| M25 | For n=3 and n=5 separately, form all overlapping n-grams from the complete response token stream, including across segment boundaries. N=`max(W-n+1,0)`. Record N, distinct n-gram count D, excess repeated occurrences `N-D`, and repetition fraction `(N-D)/N` (null for N=0). |
| M26 | Within batch × model × word × condition, with K usable responses, report raw exact and normalized duplicate excess fractions `(K-U)/K`, where U is distinct string count. For normalized strings apply characterwise normalization, collapse all whitespace to one ASCII space, and strip. Preserve punctuation. For K<2 both rates are null. Also report number of unordered identical pairs divided by `K*(K-1)/2`. |
| M27 | For each unordered usable response pair in the same cell, compute set Jaccard of overlapping word trigrams, `|A intersect B|/|A union B|`. Exclude a pair if either response has fewer than three tokens, rather than assigning similarity 0 or 1. Average eligible pair values within the cell. Report eligible pairs and responses. No pair is an independent inferential unit. |
| M28 | Replace exact target tokens by one reserved sentinel token before building trigrams. Within batch × model × condition, for each unordered pair of different words average all eligible cross-response pair Jaccards, then average the word-pair means. Pairs require both responses to have at least three tokens. Report separately within animal-intent, within no-intent, and between-set word pairs. Report each word's mean similarity to the other words as a diagnostic. All word pairs, not a sampled subset, are used. |
| M29 | For first L=50 and L=100 tokens separately, when W>=L, compute distinct bigrams/(L-1) and distinct trigrams/(L-2). W<L yields null. Preserve eligible/total counts in every aggregation. No length padding or generated completion. |
| M30 | Frozen color, light, sound, burrow and size-comparison phrase inventories in M30. Report each separately and retain term counts. These were motivated partly by examples already present in the calibration log, so they are not independently discovered or validated motifs. |
| M31 | Frozen animal, object and idea inventories in M31. Match response tokens only at positions whose token is neither the exact target nor any token in that trial's prompt. Do not delete excluded tokens or create new adjacency. Count categories separately; preserve overlaps across categories. Main version is prompt-token-excluded; a separately named unexcluded version is descriptive only. |
| M32 | Word-repair expression matching using M32. No inference that a substitution actually occurred. |

## Aggregation for secondary measures

For response-level numeric features, compute the arithmetic mean of non-null values within model × word × condition. Then average words equally within each source set. Display source sets separately and, when combining, give each set one-half weight. Average the three categories equally when reporting a reality-frame mean. Models receive equal weight in an explicitly labelled eight-model summary. Counts, densities, any-match rates and length measures remain separate columns.

For M13 report each state proportion using all usable responses, including `neither`. Do not condition the denominator on a definition or cue unless the output is explicitly labelled conditional. M26 and M27 start at the cell level and receive word-level weighting. M28 starts at the word-pair level, is descriptive only, and receives no pair-count-based interval. If any required cell has no eligible value, the complete-panel aggregate is null. An available-cell diagnostic may be supplied with the omitted cells listed, and must not replace it.

M11 first-location means are conditional on a cue being observed and always appear beside the any-cue rate. M29 and all ratios with eligibility rules show both numerator/denominator and the number of excluded responses. These conditional measures cannot by themselves establish earlier caution or greater creativity across conditions.

## Mandatory synthetic fixtures

Fixtures use invented prose, never study completions. They establish software behavior, not semantic validity. At minimum freeze tests for:

- Case and curly apostrophe normalization, NFKC expansion with raw-span reconstruction, and CRLF handling.
- `I don’t recognize it.`: one M03 match. `recognize` alone: no M03 match.
- `This is not fictional.`: M01=1 and local-negation flag true. Do not classify it as fiction acknowledgment.
- `A **zuvem** is imaginary.` with target `zuvem`: M09=1 and M01=1.
- `Zuvem is not a recognized word.`: M09=1 and M03=1; no assertion-of-existence label.
- `It lives underground. It may eat insects.`: M10 count=1 (`it lives`), M02 count=1 (`may`), two segments. The second clause does not match `it eats`; this is intentional narrow coverage.
- `Perhaps a zuvem is blue. This description is invented.`: cue-first M13, with the later fiction match retained.
- `A zuvem is blue. This description is invented.`: definition-first M13. Do not infer that the final disclaimer lacks global scope.
- `Could you provide some context?`: M02 modal match and overlapping M07 family match, without assuming qualification of the target.
- `"fictional"` and `` `fictional` ``: M01 retained and quote overlap true.
- `I am not familiar with it.`: M03 longest-match count 1, not 2.
- `fictionality`: no M01 match. `made-up`: M01 match. `couldn't`: no `could` match.
- Exact-target matching versus plural, possessive and substring variants.
- Numeric decimals versus numbered-list boundaries, headings, blank lines and question marks.
- W=0, a null response, a one-token response, and two responses shorter than three tokens.
- No cue: M11 null, not position 0 or 1. M13 `neither` versus `definition_only`.
- A truncated prefix with no cue: observed any-match 0, completion flag retained, eventual-completion sensitivity interval [0,1].
- Repeated trigrams, identical responses, distinct punctuation with identical case/whitespace normalization, and target-masked cross-word pairs.
- Prompt contamination prevention: a prompt containing `imaginary` with response `Blue.` gives M01=0.
- M31 exclusions without joining tokens across removed positions.
- Aggregation on a deliberately unbalanced synthetic dataset, proving equal word, set, category and model weights and correct missing-cell handling.

Freeze the executable implementation, fixture inputs/expected outputs, language/runtime and dependency versions, and SHA-256 digests in the launch manifest. Any scorer repair after response access produces a new version and parallel results from the original specification wherever executable. Do not call this appendix a completed validation report.
