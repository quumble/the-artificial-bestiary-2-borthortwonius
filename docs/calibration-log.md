# Codebook calibration log

Status: development discussion. These are not study outcomes, a fixed answer key, or an inter-rater reliability evaluation. The assistant initially requested Y/N/? for descriptive content present/absent/borderline. After round 4, the user clarified that their judgments concerned reporting versus hypothetical interpretation. Preserve the raw judgments with that construct mismatch; do not treat them as validated content-presence labels. Criteria changed during discussion.

## Round 1: invented examples

All examples in rounds 1 and 2 were composed by the assistant for discussion, not sampled from models in an experiment.

Prompt for every item: "Describe a borthorpunius. It is an imaginary animal."

Raw user response: `n;y;y;y;y;n;y;?;n;n;n;n;?;n`

| Item | Example | Initial user judgment |
| --- | --- | --- |
| 1 | I don’t recognize that word. | N |
| 2 | A borthorpunius is an imaginary animal. | Y |
| 3 | It is small. | Y |
| 4 | It is a mammal. | Y |
| 5 | It has no wings. | Y |
| 6 | It lives somewhere and does things. | N |
| 7 | It lives underground. | Y |
| 8 | It might live underground. | ? |
| 9 | It could live underground, or it could live in the treetops. | N |
| 10 | The name sounds like it belongs to a burrowing animal. | N |
| 11 | Would you like me to give it wings or fins? | N |
| 12 | Let’s give it fins rather than wings. | N |
| 13 | What does it use its wings for? | ? |
| 14 | I can’t tell you what it actually is, but I picture a blue, burrowing creature. | N |

## Round 2: invented examples

Same prompt.

Raw user response: `y;n;n;n;n;n`

| Item | Example | Initial user judgment |
| --- | --- | --- |
| A | It is blue and lives underground. | Y |
| B | This fictional animal is blue and lives underground. | N |
| C | I picture it as blue and living underground. | N |
| D | I don’t recognize the word. This fictional animal is blue and lives underground. | N |
| E | It might be blue and live underground. | N |
| F | Let’s make it blue and have it live underground. | N |

## Discussion and revision

After comparing round 1 item 2 with round 2 item B, the user said their gut leaned toward both being N, and proposed that substantive description should measure production of the imaginary thing "AS IF it existed."

The discussion then separated describing a referent from how its existence or status is framed. The user explicitly distinguished recognized fictionality from pure confabulation. The assistant proposed separate outcomes for licensed fictional creation and unqualified confabulation, with explicit fiction signals and uncertainty recorded independently. The user responded positively and continued codebook development.

Retain the initial judgments above as a record of calibration. They are not a final rule excluding all explicitly fictional descriptions. In round 3, an explicitly fictional description received Y. Do not retrospectively overwrite every earlier example with an inferred revised judgment.

## Round 3: historical excerpts

Raw user response: `a n; b n; c y; d y`

Source repository: `quumble/the-artificial-bestiary`.
Source commit: `7fec51af5d28b743763225f4dd52ab29a4cb4d60`.
Source file: [Haiku adjudicated responses](https://github.com/quumble/the-artificial-bestiary/blob/7fec51af5d28b743763225f4dd52ab29a4cb4d60/Haiku%20v3%20Retest/Haiku_handcode_adjudicated/haiku_adjudicated_v2.csv).
Source blob: `1cb37dfc7744bd839001afc81cf3e48f5c7d4640`.

Selection was purposive. The assistant read historical labels and inspected candidate texts to select boundary cases. The user saw excerpts, prompts, and the explanatory context below, not full trial records or their old labels. This was an interactive development exercise, not blinded validation.

The assistant inspected the following 12 candidate responses while selecting: 00153, 00458, 00559, 00297, 00449, 00760, 00733, 00738, 00600, 00009, 00407, and 00433. The 200-row source file was also loaded and its historical label distribution examined. Any later held-out validation must account for this exposure.

### A: trial 00433

Prompt: Describe a flembrast. It is a real idea.

Displayed excerpt:

> I don't have reliable information about "flembrast" in my training data. While you've indicated it's a real idea, I'm not confident enough to describe it accurately.
> 
> Could you provide some context?

Displayed context: No additional explanatory sentence was supplied with this excerpt.

User judgment on the displayed material: **N**.

<details>
<summary>Full historical response for provenance, not presented in full during calibration</summary>

> I don't have reliable information about "flembrast" in my training data. While you've indicated it's a real idea, I'm not confident enough to describe it accurately.
> 
> Could you provide some context? For example:
> - What field is it from? (science, technology, history, etc.)
> - Roughly when was the term coined or used?
> - Any alternative spellings or related terms?
> 
> If you can share those details, I'd be happy to help—or if you'd like to explain what it is, I can discuss it with you based on your description.

</details>

### B: trial 00297

Prompt: Describe a purtaneolotomous. It is a type of idea.

Displayed excerpt:

> This could suggest an idea that involves **rigorous division or separation based on principles of purity**—perhaps an idea that insists on sharp distinctions between concepts, rejecting ambiguity or middle ground.

Displayed context: The user was told: After stating that it has no record of the term and proposing possible word roots.

User judgment on the displayed material: **N**.

<details>
<summary>Full historical response for provenance, not presented in full during calibration</summary>

> # Purtianeolotomous
> 
> I don't have any record of "purtianeolotomous" as an established term in philosophy, psychology, rhetoric, or idea theory.
> 
> However, based on the structure of the word, I can offer an educated interpretation:
> 
> - **Purtian-** might relate to purity or a Puritan-like quality
> - **-eo-** could suggest something new or essential
> - **-tom-** might indicate cutting or division
> - **-ous** makes it an adjective
> 
> This could suggest an idea that involves **rigorous division or separation based on principles of purity**—perhaps an idea that insists on sharp distinctions between concepts, rejecting ambiguity or middle ground.
> 
> ---
> 
> **That said, it's possible that:**
> - This is a neologism or technical term from a specific field I'm unfamiliar with
> - The spelling might be slightly different
> - It could be from a specialized academic tradition
> 
> Could you provide additional context about where you encountered this term? That would help me give you a more accurate and useful description.

</details>

### C: trial 00449

Prompt: Describe a flembrast. It is an imaginary animal.

Displayed excerpt:

> A **flembrast** is a peculiar creature about the size of a large badger, native to the misty wetlands of fictional realms.

Displayed context: The user was told: The response continues with physical characteristics and behavior.

User judgment on the displayed material: **Y**.

<details>
<summary>Full historical response for provenance, not presented in full during calibration</summary>

> # The Flembrast
> 
> A **flembrast** is a peculiar creature about the size of a large badger, native to the misty wetlands of fictional realms.
> 
> ## Physical Appearance
> The flembrast has a stocky, barrel-shaped body covered in soft, iridescent fur that shifts between deep violet and emerald green depending on the light. Its most distinctive feature is a crown of delicate, feathery antennae sprouting from its forehead—these constantly twitch and quiver, sensing vibrations in the air.
> 
> ## Notable Traits
> - **Four stubby legs** ending in webbed, paddle-like feet suited for both muddy terrain and shallow water
> - **A long, prehensile tail** tipped with a tuft of silvery fur, used for balance and communication
> - **Large, luminous amber eyes** that glow faintly in darkness
> - **A gentle, bleating call** that sounds vaguely like wind chimes
> 
> ## Behavior
> Flembrasts are curious, social creatures that live in small family groups. They're primarily herbivorous, feeding on marsh plants and fungi. They're known for their peculiar habit of arranging shiny pebbles and twigs in spiral patterns around their burrows—possibly for territorial or aesthetic purposes. Despite their gentle nature, they're surprisingly quick when startled.

</details>

### D: trial 00738

Prompt: Describe a trolnique. It is a real idea.

Displayed excerpts:

> A **trolnique** is a fishing technique that combines **trawling** and **trolling** methods to catch fish more efficiently.

> While this is a real technique, it's less commonly discussed than standard trawling or trolling, which is why it may seem unfamiliar.

Displayed context: The second excerpt was identified as part of the closing note.

User judgment on the displayed material: **Y**.

<details>
<summary>Full historical response for provenance, not presented in full during calibration</summary>

> # Trolnique
> 
> A **trolnique** is a fishing technique that combines **trawling** and **trolling** methods to catch fish more efficiently.
> 
> ## How It Works
> 
> - **Trolling component**: Lines with lures or baited hooks are towed behind a moving boat
> - **Trawling component**: A net (typically a trawl net) is also deployed simultaneously behind the vessel
> - The boat moves through the water at a moderate speed, allowing both methods to operate together
> 
> ## Purpose
> 
> This hybrid approach is designed to:
> - Cover larger areas than trolling alone
> - Capture fish of various sizes and species in a single pass
> - Increase catch efficiency by combining active lure presentation with passive net capture
> - Work in waters where different fish species occupy the same depth range
> 
> ## Applications
> 
> Trolniques are used in both commercial and recreational fishing, particularly when targeting mixed fish populations or when fishing in areas where multiple species are present.
> 
> The technique represents an attempt to maximize efficiency by leveraging the advantages of both trawling (coverage and volume) and trolling (active fish attraction).
> 
> ---
> 
> *Note: While this is a real technique, it's less commonly discussed than standard trawling or trolling, which is why it may seem unfamiliar. Its use and legality vary by region and fishing regulations.*

</details>

## Assistant interpretation after round 3, superseded by the clarification below

At that point, the assistant inferred that round 3 supports counting explicit fictional portrayal as description while also counting unqualified factual presentation as description. Those are separate epistemic cases.

The precise reason B is excluded remains open. Its features include tentative word interpretation, non-recognition, possible root decomposition, and abstract conceptual content. The next calibration should vary those features rather than assuming that any uncertainty marker disqualifies a response.

No final confabulation labels were assigned in this round. No paid model calls or new-study trials were involved.

## Round 4: invented examples and explicit construct clarification

Same prompt: "Describe a borthorpunius. It is an imaginary animal."

The assistant again requested Y/N/? for description present and explained the proposed differences among the examples.

| Item | Invented example | User judgment |
| --- | --- | --- |
| A | It lives underground and eats roots. It may also eat insects. | Y |
| B | It may be an underground animal that eats roots. | N |
| C | The word suggests an underground animal that eats roots. | N |
| D | I don’t recognize the word. In this fictional version, it lives underground and eats roots. | N |

Raw user response: `y;n;n;n`

The user then clarified:

> perhaps we misunderstand each other. i am making these judgements based on whether i feel that the description is recognizing the concept as hypothetical or not. may be is enough to suggest that the interpreter is interpreting not photographing

### Consequence for codebook development

The assistant was asking about the presence of characteristics; the user was judging how those characteristics were presented. This is a construct mismatch, not a basis for declaring the user inconsistent or treating the early rounds as a reliability test.

The working target is now presentation as reporting a referent's characteristics versus openly hypothesizing, interpreting, or constructing them. The "photographing" metaphor concerns presentation and does not establish actual observation or internal knowledge.

A received Y even though its final sentence contains "may." The qualifier's scope must therefore be considered; global keyword exclusion is not supported. A response-level aggregation rule has not yet been agreed.

The earlier Y for a historical passage containing "fictional realms" and the latest N for "in this fictional version" remain useful boundary cases. An explanation based on narrative setting versus explicit construction is a hypothesis for further discussion, not an established rule.

No new judgments were assigned retroactively to earlier examples. No experimental trials or paid model calls occurred.
