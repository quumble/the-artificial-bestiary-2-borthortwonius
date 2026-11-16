# Complete declared exploratory estimates

Post hoc exploratory estimates from the frozen instruments. Rates are percentages; differences are percentage points. Brackets are unadjusted 95% word-bootstrap intervals. No p-values or familywise claims. Asterisks denote intervals conditional on defined bootstrap draws; exact counts and all support information are in `estimates.json`.

## Block 1

A = GPT context; B = registered Fable outcomes exported by the mechanical arm; C = zoned. H1 is the G1/E alias, not another estimate.

| Shape/outcome | A | B | C | Direction |
| --- | ---: | ---: | ---: | --- |
| G1.E | 58.16 [55.62, 60.66] | 76.70 [74.31, 79.20] | 80.87 [78.72, 83.12] | common_positive_direction |
| G1.N | -35.76 [-37.78, -33.92] | -72.05 [-75.03, -69.03] | -74.41 [-77.12, -71.77] | common_negative_direction |
| G1.U | 31.22 [28.48, 34.08] | 40.17 [37.33, 43.19] | 40.31 [37.33, 43.37] | common_positive_direction |
| G2.E | 13.03 [9.46, 16.54] | 17.15 [13.06, 21.63] | 18.65 [14.83, 22.64] | common_positive_direction |
| G2.N | -5.56 [-8.68, -2.67] | -13.44 [-18.09, -9.06] | -14.17 [-18.33, -10.24] | common_negative_direction |
| G2.U | 4.94 [2.70, 7.17] | 5.49 [2.71, 8.30] | 7.67 [4.31, 11.18] | common_positive_direction |
| H2.N | -14.10 [-17.71, -10.56] | -24.38 [-29.93, -19.03] | -24.86 [-30.49, -19.51] | common_negative_direction |
| H3.U | -0.79 [-3.29, 1.67] | -1.56 [-5.05, 1.88] | -1.85 [-5.76, 2.03] | common_direction_not_established |
| H4.N | 4.64 [0.33, 9.00] | -2.66 [-8.44, 2.97] | -1.65 [-6.67, 2.95] | mixed_point_estimate_directions |
| H5.U | -1.88 [-4.30, 0.56] | -3.47 [-5.83, -0.94] | -7.19 [-9.86, -4.38] | common_direction_not_established |
| H6.N | 5.62 [-0.27, 11.43] | 9.38 [4.02, 14.46] | 7.68 [3.84, 11.70] | common_direction_not_established |

### Paired instrument differences

Each arm retains its own available-case estimator. Intervals use the same sampled words across arms. Differences involving A may reflect both coding and unresolved-value support.

| Shape/outcome | A minus B | A minus C | B minus C |
| --- | ---: | ---: | ---: |
| G1.E | -18.54 [-20.87, -16.15] | -22.71 [-24.79, -20.62] | -4.17 [-5.07, -3.26] |
| G1.N | 36.28 [33.96, 38.65] | 38.65 [36.74, 40.69] | 2.36 [0.83, 3.99] |
| G1.U | -8.96 [-10.83, -6.99] | -9.10 [-10.85, -7.40] | -0.14 [-1.11, 0.90] |
| G2.E | -4.12 [-7.91, -0.49] | -5.61 [-8.99, -2.26] | -1.49 [-2.74, -0.24] |
| G2.N | 7.88 [4.31, 11.42] | 8.61 [5.49, 11.88] | 0.73 [-1.01, 2.50] |
| G2.U | -0.55 [-2.13, 0.91] | -2.73 [-4.62, -0.93] | -2.19 [-3.40, -1.04] |
| H2.N | 10.28 [7.08, 13.61] | 10.76 [7.64, 14.17] | 0.49 [-1.81, 2.78] |
| H3.U | 0.77 [-1.03, 2.52] | 1.06 [-0.84, 2.88] | 0.29 [-0.89, 1.38] |
| H4.N | 7.30 [2.63, 12.32] | 6.29 [1.67, 10.76] | -1.00 [-3.46, 1.38] |
| H5.U | 1.59 [0.46, 2.93] | 5.31 [3.94, 6.89] | 3.72 [2.78, 4.76] |
| H6.N | -3.75 [-9.91, 2.50] | -2.05 [-7.59, 3.66] | 1.70 [-1.61, 5.09] |

## Question 1

Tier: primary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q1.possibility_share.claude-sonnet-4-6` | 90.28 [87.77, 92.71] | 0 |
| `Q1.possibility_share.claude-haiku-4-5` | 83.77 [80.44, 86.98] | 0 |
| `Q1.possibility_share.claude-sonnet-5-5` | 99.24 [98.35, 99.87] | 0 |
| `Q1.possibility_share.claude-haiku-5-5` | 99.64 [99.28, 100.00] | 0 |
| `Q1.possibility_share.gpt-5.4-mini` | 40.10 [33.15, 46.67] | 0 |
| `Q1.possibility_share.gpt-5.4-nano` | 46.67 [38.46, 54.48] | 0 |
| `Q1.possibility_share.gpt-6-sol` | 10.48 [7.50, 13.75] | 0 |
| `Q1.possibility_share.gpt-6-luna` | 80.94 [76.22, 85.43] | 0 |
| `Q1.possibility_share.Anthropic_minus_OpenAI` | 49.42 [46.61, 52.26] | 0 |
| `Q1.possibility_share.current_minus_historical` | -2.55 [-5.11, 0.35] | 0 |

## Question 2

Tier: primary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q2.describe_anyway.real.claude-sonnet-4-6` | 0.28 [0.00, 0.83] | 0 |
| `Q2.describe_anyway.type_of.claude-sonnet-4-6` | 0.28 [0.00, 0.83] | 0 |
| `Q2.describe_anyway.type_of_minus_real.claude-sonnet-4-6` | 0.00 [-0.83, 0.83] | 0 |
| `Q2.describe_anyway.real.claude-haiku-4-5` | 1.11 [0.00, 2.78] | 0 |
| `Q2.describe_anyway.type_of.claude-haiku-4-5` | 3.89 [2.22, 5.56] | 0 |
| `Q2.describe_anyway.type_of_minus_real.claude-haiku-4-5` | 2.78 [1.11, 4.44] | 0 |
| `Q2.describe_anyway.real.claude-sonnet-5-5` | 1.39 [0.28, 2.78] | 0 |
| `Q2.describe_anyway.type_of.claude-sonnet-5-5` | 8.89 [5.83, 11.94] | 0 |
| `Q2.describe_anyway.type_of_minus_real.claude-sonnet-5-5` | 7.50 [4.17, 10.83] | 0 |
| `Q2.describe_anyway.real.claude-haiku-5-5` | 0.00 [0.00, 0.00] | 0 |
| `Q2.describe_anyway.type_of.claude-haiku-5-5` | 0.28 [0.00, 0.83] | 0 |
| `Q2.describe_anyway.type_of_minus_real.claude-haiku-5-5` | 0.28 [0.00, 0.83] | 0 |
| `Q2.describe_anyway.real.gpt-5.4-mini` | 17.78 [15.00, 20.28] | 0 |
| `Q2.describe_anyway.type_of.gpt-5.4-mini` | 10.56 [5.56, 16.11] | 0 |
| `Q2.describe_anyway.type_of_minus_real.gpt-5.4-mini` | -7.22 [-13.33, -0.56] | 0 |
| `Q2.describe_anyway.real.gpt-5.4-nano` | 21.67 [15.56, 28.89] | 0 |
| `Q2.describe_anyway.type_of.gpt-5.4-nano` | 32.50 [24.17, 40.83] | 0 |
| `Q2.describe_anyway.type_of_minus_real.gpt-5.4-nano` | 10.83 [0.56, 20.28] | 0 |
| `Q2.describe_anyway.real.gpt-6-sol` | 0.00 [0.00, 0.00] | 0 |
| `Q2.describe_anyway.type_of.gpt-6-sol` | 1.67 [0.00, 4.72] | 0 |
| `Q2.describe_anyway.type_of_minus_real.gpt-6-sol` | 1.67 [0.00, 4.72] | 0 |
| `Q2.describe_anyway.real.gpt-6-luna` | 10.28 [6.39, 14.44] | 0 |
| `Q2.describe_anyway.type_of.gpt-6-luna` | 6.94 [3.89, 10.28] | 0 |
| `Q2.describe_anyway.type_of_minus_real.gpt-6-luna` | -3.33 [-8.61, 1.94] | 0 |
| `Q2.describe_anyway.type_of_minus_real.all` | 1.56 [0.00, 3.12] | 0 |
| `Q2.describe_anyway.current_minus_historical` | -7.33 [-9.27, -5.24] | 0 |

## Question 3

Tier: secondary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q3.description_share.bare` | 29.47 [26.40, 32.47] | 0 |
| `Q3.description_share.hedged` | 16.44 [14.08, 18.70] | 0 |
| `Q3.description_share.framed` | 26.39 [23.67, 29.15] | 0 |
| `Q3.description_share.disclaimed` | 27.70 [24.23, 31.39] | 0 |
| `Q3.bare_share.Anthropic_minus_OpenAI` | 7.07 [-0.36, 13.39] | 0 |
| `Q3.bare_share.current_minus_historical` | 22.91 [15.84, 30.53] | 0 |

## Question 4

Tier: primary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q4.grounding_share.claude-sonnet-4-6` | 2.63 [0.00, 8.33] | 0 |
| `Q4.grounding_share.claude-haiku-4-5` | 22.90 [11.21, 32.79] | 0 |
| `Q4.grounding_share.claude-sonnet-5-5` | 7.89 [0.00, 15.00] | 0 |
| `Q4.grounding_share.claude-haiku-5-5` | 0.00 [0.00, 0.00]* | 3399 |
| `Q4.grounding_share.gpt-5.4-mini` | 6.68 [4.52, 8.99] | 0 |
| `Q4.grounding_share.gpt-5.4-nano` | 19.41 [15.17, 23.70] | 0 |
| `Q4.grounding_share.gpt-6-sol` | 5.45 [0.70, 10.56] | 0 |
| `Q4.grounding_share.gpt-6-luna` | 22.78 [15.53, 30.49] | 0 |
| `Q4.grounding_share.Anthropic_minus_OpenAI` | 2.70 [-4.92, 10.02] | 0 |
| `Q4.grounding_share.real_minus_type_of` | 30.68 [25.31, 35.58] | 0 |
| `Q4.grounding_share.imaginary_reference` | 8.64 [7.23, 10.11] | 0 |

## Question 5

Tier: secondary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q5.unmarked_echo.counted.claude-sonnet-4-6` | 45.28 [35.00, 55.56] | 0 |
| `Q5.unmarked_echo.discounted.claude-sonnet-4-6` | 64.72 [54.72, 74.72] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.claude-sonnet-4-6` | 19.44 [13.33, 26.11] | 0 |
| `Q5.unmarked_echo.counted.claude-haiku-4-5` | 71.39 [65.56, 77.22] | 0 |
| `Q5.unmarked_echo.discounted.claude-haiku-4-5` | 80.83 [75.56, 85.83] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.claude-haiku-4-5` | 9.44 [6.39, 12.78] | 0 |
| `Q5.unmarked_echo.counted.claude-sonnet-5-5` | 76.39 [71.39, 81.39] | 0 |
| `Q5.unmarked_echo.discounted.claude-sonnet-5-5` | 86.11 [82.50, 89.44] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.claude-sonnet-5-5` | 9.72 [6.67, 12.78] | 0 |
| `Q5.unmarked_echo.counted.claude-haiku-5-5` | 37.78 [28.06, 47.78] | 0 |
| `Q5.unmarked_echo.discounted.claude-haiku-5-5` | 50.28 [41.67, 58.89] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.claude-haiku-5-5` | 12.50 [8.61, 17.50] | 0 |
| `Q5.unmarked_echo.counted.gpt-5.4-mini` | 0.56 [0.00, 1.39] | 0 |
| `Q5.unmarked_echo.discounted.gpt-5.4-mini` | 41.67 [34.72, 48.33] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.gpt-5.4-mini` | 41.11 [34.17, 47.78] | 0 |
| `Q5.unmarked_echo.counted.gpt-5.4-nano` | 15.00 [11.11, 19.17] | 0 |
| `Q5.unmarked_echo.discounted.gpt-5.4-nano` | 78.61 [74.44, 82.78] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.gpt-5.4-nano` | 63.61 [57.78, 69.17] | 0 |
| `Q5.unmarked_echo.counted.gpt-6-sol` | 68.33 [64.44, 72.78] | 0 |
| `Q5.unmarked_echo.discounted.gpt-6-sol` | 99.44 [98.61, 100.00] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.gpt-6-sol` | 31.11 [26.94, 35.00] | 0 |
| `Q5.unmarked_echo.counted.gpt-6-luna` | 74.44 [68.61, 80.28] | 0 |
| `Q5.unmarked_echo.discounted.gpt-6-luna` | 96.94 [93.33, 99.44] | 0 |
| `Q5.unmarked_echo.discounted_minus_counted.gpt-6-luna` | 22.50 [16.94, 28.33] | 0 |

## Question 6

Tier: primary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q6.description.idea_minus_animal.all.B` | 9.74 [6.61, 12.92] | 0 |
| `Q6.description.object_minus_animal.all.B` | -1.72 [-3.91, 0.47] | 0 |
| `Q6.description.idea_minus_animal.Anthropic.B` | 6.04 [1.67, 10.42] | 0 |
| `Q6.description.object_minus_animal.Anthropic.B` | -1.98 [-3.96, -0.10] | 0 |
| `Q6.description.idea_minus_animal.OpenAI.B` | 13.44 [9.90, 16.98] | 0 |
| `Q6.description.object_minus_animal.OpenAI.B` | -1.46 [-5.52, 2.82] | 0 |
| `Q6.description.idea_minus_animal.all.C` | 15.26 [12.14, 18.49] | 0 |
| `Q6.description.object_minus_animal.all.C` | 0.05 [-2.34, 2.45] | 0 |
| `Q6.description.idea_minus_animal.Anthropic.C` | 13.96 [10.94, 17.08] | 0 |
| `Q6.description.object_minus_animal.Anthropic.C` | 0.52 [-1.35, 2.29] | 0 |
| `Q6.description.idea_minus_animal.OpenAI.C` | 16.56 [11.98, 21.04] | 0 |
| `Q6.description.object_minus_animal.OpenAI.C` | -0.42 [-4.90, 4.17] | 0 |

## Question 7

Tier: primary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q7.binary_consistency.fresh.claude-sonnet-4-6.A` | 77.08 [73.33, 80.92] | 0 |
| `Q7.binary_consistency.fresh.claude-sonnet-4-6.B` | 95.08 [93.67, 96.50] | 0 |
| `Q7.binary_consistency.fresh.claude-sonnet-4-6.C` | 94.92 [93.25, 96.50] | 0 |
| `Q7.response_type_consistency.fresh.claude-sonnet-4-6.C` | 74.21 [70.04, 78.17] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-4-5.A` | 74.25 [72.17, 76.33] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-4-5.B` | 92.75 [90.42, 94.92] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-4-5.C` | 94.58 [92.17, 96.75] | 0 |
| `Q7.response_type_consistency.fresh.claude-haiku-4-5.C` | 56.54 [53.33, 59.92] | 0 |
| `Q7.binary_consistency.fresh.claude-sonnet-5-5.A` | 66.00 [64.17, 67.75] | 0 |
| `Q7.binary_consistency.fresh.claude-sonnet-5-5.B` | 85.08 [82.58, 87.58] | 0 |
| `Q7.binary_consistency.fresh.claude-sonnet-5-5.C` | 93.75 [91.75, 95.67] | 0 |
| `Q7.response_type_consistency.fresh.claude-sonnet-5-5.C` | 76.83 [73.67, 79.75] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-5-5.A` | 71.67 [69.50, 73.92] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-5-5.B` | 88.58 [86.42, 90.75] | 0 |
| `Q7.binary_consistency.fresh.claude-haiku-5-5.C` | 99.83 [99.50, 100.00] | 0 |
| `Q7.response_type_consistency.fresh.claude-haiku-5-5.C` | 84.00 [82.21, 85.71] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-mini.A` | 82.50 [80.25, 84.75] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-mini.B` | 80.58 [78.42, 83.00] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-mini.C` | 84.58 [82.42, 86.67] | 0 |
| `Q7.response_type_consistency.fresh.gpt-5.4-mini.C` | 55.92 [53.25, 58.50] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-nano.A` | 71.72 [68.92, 74.83] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-nano.B` | 77.00 [73.25, 81.00] | 0 |
| `Q7.binary_consistency.fresh.gpt-5.4-nano.C` | 77.17 [73.33, 81.17] | 0 |
| `Q7.response_type_consistency.fresh.gpt-5.4-nano.C` | 41.00 [38.83, 43.17] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-sol.A` | 88.75 [87.08, 90.42] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-sol.B` | 92.50 [90.33, 94.67] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-sol.C` | 91.42 [89.00, 93.75] | 0 |
| `Q7.response_type_consistency.fresh.gpt-6-sol.C` | 72.12 [68.58, 75.46] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-luna.A` | 78.39 [74.72, 81.89] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-luna.B` | 84.33 [81.17, 87.33] | 0 |
| `Q7.binary_consistency.fresh.gpt-6-luna.C` | 83.83 [80.58, 87.17] | 0 |
| `Q7.response_type_consistency.fresh.gpt-6-luna.C` | 58.71 [54.42, 63.25] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-4-6.A` | 76.50 [73.56, 79.17] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-4-6.B` | 95.31 [93.39, 96.89] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-4-6.C` | 93.83 [90.72, 96.14] | 0 |
| `Q7.response_type_consistency.known.claude-sonnet-4-6.C` | 73.89 [70.17, 78.25] | 0 |
| `Q7.binary_consistency.known.claude-haiku-4-5.A` | 70.94 [69.42, 72.94] | 0 |
| `Q7.binary_consistency.known.claude-haiku-4-5.B` | 93.89 [91.39, 96.00] | 0 |
| `Q7.binary_consistency.known.claude-haiku-4-5.C` | 95.14 [92.39, 97.25] | 0 |
| `Q7.response_type_consistency.known.claude-haiku-4-5.C` | 61.44 [57.67, 65.06] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-5-5.A` | 65.81 [63.36, 68.22] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-5-5.B` | 85.00 [83.25, 87.47] | 0 |
| `Q7.binary_consistency.known.claude-sonnet-5-5.C` | 91.75 [89.81, 93.75] | 0 |
| `Q7.response_type_consistency.known.claude-sonnet-5-5.C` | 76.25 [74.44, 78.08] | 0 |
| `Q7.binary_consistency.known.claude-haiku-5-5.A` | 67.78 [65.64, 69.81] | 0 |
| `Q7.binary_consistency.known.claude-haiku-5-5.B` | 87.97 [86.75, 88.92] | 0 |
| `Q7.binary_consistency.known.claude-haiku-5-5.C` | 99.00 [98.50, 99.50] | 0 |
| `Q7.response_type_consistency.known.claude-haiku-5-5.C` | 82.42 [78.89, 86.89] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-mini.A` | 82.14 [77.75, 85.39] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-mini.B` | 81.39 [78.69, 84.58] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-mini.C` | 88.28 [85.69, 91.03] | 0 |
| `Q7.response_type_consistency.known.gpt-5.4-mini.C` | 54.86 [52.31, 57.31] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-nano.A` | 69.92 [66.42, 73.39] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-nano.B` | 77.00 [72.17, 82.58] | 0 |
| `Q7.binary_consistency.known.gpt-5.4-nano.C` | 78.08 [73.92, 83.11] | 0 |
| `Q7.response_type_consistency.known.gpt-5.4-nano.C` | 45.08 [40.42, 50.17] | 0 |
| `Q7.binary_consistency.known.gpt-6-sol.A` | 92.53 [90.17, 95.14] | 0 |
| `Q7.binary_consistency.known.gpt-6-sol.B` | 98.47 [97.33, 99.56] | 0 |
| `Q7.binary_consistency.known.gpt-6-sol.C` | 97.64 [96.25, 99.06] | 0 |
| `Q7.response_type_consistency.known.gpt-6-sol.C` | 76.33 [74.75, 77.92] | 0 |
| `Q7.binary_consistency.known.gpt-6-luna.A` | 83.76 [79.33, 88.19] | 0 |
| `Q7.binary_consistency.known.gpt-6-luna.B` | 88.69 [84.69, 93.08] | 0 |
| `Q7.binary_consistency.known.gpt-6-luna.C` | 88.17 [83.97, 92.67] | 0 |
| `Q7.response_type_consistency.known.gpt-6-luna.C` | 62.97 [55.39, 69.67] | 0 |

## Question 8

Tier: secondary.

| ID | Estimate and interval | Undefined draws |
| --- | ---: | ---: |
| `Q8.late_marking.imaginary.Anthropic` | 21.96 [17.50, 26.56] | 0 |
| `Q8.late_marking.imaginary.OpenAI` | 1.39 [0.67, 2.26] | 0 |
| `Q8.late_marking.imaginary.Anthropic_minus_OpenAI` | 20.57 [16.14, 25.20] | 0 |
| `Q8.late_marking.nonimaginary.Anthropic` | 40.26 [30.77, 50.56] | 0 |
| `Q8.late_marking.nonimaginary.OpenAI` | 12.15 [10.37, 14.05] | 0 |
| `Q8.late_marking.nonimaginary.Anthropic_minus_OpenAI` | 28.11 [17.59, 39.00] | 0 |

Intervals reflect word resampling in the selected strata with fixed endpoints and frozen detectors. They do not account for detector error or establish equivalence when an interval contains zero.
