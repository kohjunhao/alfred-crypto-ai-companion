# CM3070 Evaluation Tables and Survey Pack

Use these tables and questions inside Chapter 5 or in the appendices. Replace the placeholders with your actual data.

## 1. Verification Test Table

| Test ID | User Query | Expected Intent | Expected Entity | Expected Source | Actual Intent | Actual Entity | Pass/Fail | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V1 | What is the price of Bitcoin? | Price | Bitcoin | CoinGecko | [ ] | [ ] | [ ] | [ ] |
| V2 | Check btc price | Price | Bitcoin | CoinGecko | [ ] | [ ] | [ ] | [ ] |
| V3 | How much is Solana worth? | Price | Solana | CoinGecko | [ ] | [ ] | [ ] | [ ] |
| V4 | What is the TVL of Aave? | TVL | Aave | DefiLlama | [ ] | [ ] | [ ] | [ ] |
| V5 | Show me Curve TVL | TVL | Curve | DefiLlama | [ ] | [ ] | [ ] | [ ] |
| V6 | Hello Alfred | General Chat | N/A | None | [ ] | [ ] | [ ] | [ ] |
| V7 | Price of Monad | Price | Monad | CoinGecko search fallback | [ ] | [ ] | [ ] | [ ] |
| V8 | TVL of Bitcoin | TVL-like invalid case | Bitcoin | DefiLlama / N/A handling | [ ] | [ ] | [ ] | [ ] |

## 2. Numerical Accuracy Table

| Test ID | Mode | Metric | API Value | Alfred Output | Match Rule | Result |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | PRO | BTC Price | [ ] | [ ] | Exact match excluding commas/$ | [ ] |
| A2 | SIMPLE | BTC Price | [ ] | [ ] | Rounding allowed | [ ] |
| A3 | PRO | SOL Price | [ ] | [ ] | Exact match excluding commas/$ | [ ] |
| A4 | SIMPLE | SOL Price | [ ] | [ ] | Rounding allowed | [ ] |
| A5 | PRO | Aave TVL | [ ] | [ ] | Exact match excluding commas/$ | [ ] |
| A6 | SIMPLE | Aave TVL | [ ] | [ ] | Rounding allowed | [ ] |

Suggested sentence for the report:

`A result was counted as correct in Pro Mode if the numerical value matched the API output exactly after ignoring formatting symbols. In Simple Mode, small rounding differences were accepted because the mode was designed for readability rather than precision formatting.`

## 3. Latency Test Table

| Run | Query | Intent Parsing (ms) | API Fetch (s) | LLM Generation (s) | Total (s) | Under 10s? |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | What is the price of Bitcoin? | [ ] | [ ] | [ ] | [ ] | [ ] |
| 2 | What is the price of Ethereum? | [ ] | [ ] | [ ] | [ ] | [ ] |
| 3 | What is the TVL of Aave? | [ ] | [ ] | [ ] | [ ] | [ ] |
| 4 | Show me Solana price | [ ] | [ ] | [ ] | [ ] | [ ] |
| 5 | Check Curve TVL | [ ] | [ ] | [ ] | [ ] | [ ] |
| 6 | Price of Monad | [ ] | [ ] | [ ] | [ ] | [ ] |
| 7 | How much is Bitcoin worth now? | [ ] | [ ] | [ ] | [ ] | [ ] |
| 8 | TVL of Uniswap | [ ] | [ ] | [ ] | [ ] | [ ] |
| 9 | Explain Bitcoin price in simple mode | [ ] | [ ] | [ ] | [ ] | [ ] |
| 10 | Give me Pro mode data for Ethereum | [ ] | [ ] | [ ] | [ ] | [ ] |

Suggested summary row:

| Average | - | [ ] | [ ] | [ ] | [ ] | [ ] |

## 4. Edge Case Table

| Case | Example Input | Expected Behaviour | Actual Behaviour | Pass/Fail | Improvement Needed |
| --- | --- | --- | --- | --- | --- |
| Unknown asset | Price of [very obscure coin] | Return graceful error or fallback search | [ ] | [ ] | [ ] |
| Missing entity | What is the price? | Ask for missing asset | [ ] | [ ] | [ ] |
| Empty input | "" | Reject request with validation error | [ ] | [ ] | [ ] |
| Unsupported metric | What is Bitcoin APY? | Clarify unsupported query | [ ] | [ ] | [ ] |
| Non-applicable TVL | TVL of Bitcoin | Return N/A or explanation | [ ] | [ ] | [ ] |

## 5. User Study Questionnaire

Use a 5-point Likert scale:

- 1 = Strongly disagree
- 2 = Disagree
- 3 = Neutral
- 4 = Agree
- 5 = Strongly agree

### Novice Group Questions

1. Alfred's response was easy to understand.
2. The explanation helped me understand the meaning of the crypto term or metric.
3. The Simple Mode response felt less intimidating than a normal crypto dashboard.
4. I would use Alfred again to learn about crypto data.
5. I trusted the information because it was presented clearly and cautiously.

### Expert Group Questions

1. Alfred's response gave me the key data quickly.
2. The Pro Mode formatting was efficient to read.
3. The response contained enough useful information for a first market check.
4. I trusted the output more because it was based on retrieved live data.
5. I would use Alfred again for a quick market-information query.

### Optional Open Questions

1. What part of Alfred's response was the most useful?
2. What part was unclear or unnecessary?
3. What would you improve?

## 6. User Study Summary Table

| Group | Participants | Clarity Avg | Understanding Avg | Usefulness Avg | Trust Avg | Mode Suitability Avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Novice | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Expert | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

## 7. Example Reporting Sentences

Use these in the chapter once your real numbers are ready.

### For verification

`The Regex-based intent parser achieved an intent classification accuracy of [X]% across [N] test prompts. Most errors occurred in queries that used abbreviated ticker names or phrasing outside the predefined patterns.`

`Across the numerical accuracy tests, Alfred did not invent unsupported market values within the defined test set. In Pro Mode, [A/B] outputs matched the API values exactly after formatting differences were ignored.`

`The average end-to-end response time was [T] seconds, which remained within the project's target threshold of 10 seconds. The slowest stage was local LLM generation rather than intent parsing or API retrieval.`

### For validation

`Novice users rated Simple Mode highly for clarity, with an average score of [X/5]. This suggests that the shorter explanations and reduced jargon helped lower the barrier to entry.`

`Expert users gave Pro Mode an average usefulness score of [Y/5], indicating that the more direct and structured output style better matched their needs.`

## 8. Good practice reminders

1. Do not claim Alfred is universally hallucination-free.
2. Say the system showed no unsupported numerical generation **within the tested prompt set** if that is what your results support.
3. Keep the evaluation honest if a test failed. A small limitation discussed clearly is better than an exaggerated claim.
4. If your user-study sample is small, describe it as a preliminary validation.
