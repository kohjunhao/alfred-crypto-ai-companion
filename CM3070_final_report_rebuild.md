# CM3070 Final Report Rebuild Pack

This file converts the current preliminary report into a final-report-ready plan.

## 1. What I found after reading the folder

The folder currently contains:

- `CM3070 Final Prelim Report Koh Jun Hao.pdf`
- `CM3070 Final Project Report template.docx`
- CM3070 lecture PDFs
- a consent form template

There are no Python source files in this folder, so the best immediate move is to improve the report structure and prepare the missing final chapters.

## 2. Main gaps in the current report

Your project idea is strong. The problem statement is clear, the architecture makes sense, and the Simple/Pro split is easy to justify academically. The biggest issues are structural rather than conceptual.

### Priority issues

1. The report is still a **preliminary report**, not a **final report**.
2. Chapter 4 is titled **Feature Prototype**, but the final template requires **Implementation**.
3. There is **no separate Evaluation chapter** yet.
4. There is **no Conclusion chapter** yet.
5. The appendices and references are numbered as Chapters 5 and 6, but in the final report they should come **after** the six mandatory chapters.
6. Some claims are currently too absolute for academic writing, for example a blanket **0% hallucination** claim without a clearly defined test scope.
7. The design chapter is slightly long and can be trimmed.
8. The appendix labels for the system prompts appear to be swapped:
   - `A.1 Simple Mode Prompt` contains `"PRO"`
   - `A.2 Pro Mode Prompt` contains `"SIMPLE"`

## 3. Best rebuild strategy

Do not rewrite everything from scratch. Reuse the strongest parts of the prelim report and restructure them.

### Recommended final chapter map

1. **Introduction**
   - Reuse most of current Chapter 1.
   - Tighten wording and remove repetition.

2. **Literature Review**
   - Reuse most of current Chapter 2.
   - Strengthen synthesis between sources.
   - Keep focus on misinformation, fragmentation, hallucination, accessibility, and why Alfred is needed.

3. **Project Design**
   - Reuse current Chapter 3.
   - Trim the planning section slightly.
   - Keep architecture, user groups, stack justification, and evaluation plan.

4. **Implementation**
   - Rename current Chapter 4 from `Feature Prototype` to `Implementation`.
   - Expand code-level explanation.
   - Show the important modules:
     - `routes.py`
     - `intent_parser.py`
     - `data_fetcher.py`
     - `llm_engine.py`
   - Add more implementation detail than screenshots alone.

5. **Evaluation**
   - New chapter.
   - Split into verification and validation.
   - Verification:
     - intent parser correctness
     - historical ground-truth checks for price and TVL outputs
     - latency measurements
   - Validation:
     - novice and expert user testing
     - Likert-scale responses
     - short qualitative comments

6. **Conclusion**
   - New chapter.
   - Summarize what Alfred achieved, what it did not achieve, limitations, and future work.

7. **Appendices**
   - Keep prompts, sample JSON, regex rules, extended tables, screenshots, test logs, survey forms, and ethics materials here.

8. **References**
   - Reformat into one consistent citation style.

## 4. Word-budget plan

The lectures and template both point to a strict overall maximum of **9,500 words**, even though the individual chapter ceilings add up to more than that.

Use this practical target:

| Chapter | Target Words |
| --- | ---: |
| Introduction | 850-950 |
| Literature Review | 1,900-2,200 |
| Project Design | 1,700-1,900 |
| Implementation | 1,400-1,700 |
| Evaluation | 1,800-2,100 |
| Conclusion | 500-700 |
| **Total** | **8,150-9,550** |

Aim for about **8,800 to 9,200 words** so you have space for final edits.

## 5. Section-by-section advice

### Chapter 1: Introduction

Keep:

- problem context
- knowledge cut-off issue
- motivation for live data
- Simple/Pro mode rationale
- aims, research questions, deliverables

Improve:

- reduce repeated mentions of Flask, Ollama, and APIs
- avoid informal phrases like "fixes three issues"
- define Alfred once, then stay concise

### Chapter 2: Literature Review

Keep:

- misinformation
- fragmented market data
- knowledge cut-off and hallucination
- barriers to entry
- comparison with existing tools
- Agentic RAG and CoT

Improve:

- explicitly compare sources rather than listing them one by one
- add stronger transition lines such as:
  - "Taken together, these studies show..."
  - "This gap is important because..."
  - "In Alfred, this leads to the design choice of..."
- be careful not to oversell CoT as a guarantee of accuracy

### Chapter 3: Project Design

Keep:

- user groups
- architecture
- data flow
- technical stack
- evaluation plan

Trim:

- repeated explanation of the same layers
- long justifications for Flask and Tailwind
- Gantt discussion can be shorter in the main text if the chart is moved to an appendix

### Chapter 4: Implementation

The current chapter is a good start, but it still reads like a prototype write-up.

Strengthen it by:

- renaming it to `Implementation`
- explaining the actual logic of each module in a more code-focused way
- including how errors are handled
- showing why regex routing was chosen over a probabilistic classifier
- explaining concurrent API fetching as a latency decision
- showing how the prompt changes between modes without changing the data source

### Chapter 5: Evaluation

This is the most important missing chapter.

Your Evaluation chapter should explicitly separate:

- **Verification**: whether Alfred works correctly
- **Validation**: whether Alfred is useful for the intended users

That distinction will make the chapter feel much more rigorous.

### Chapter 6: Conclusion

This should not just repeat the introduction. It should answer:

- What was built?
- What was learned?
- What were the main strengths?
- What are the current limitations?
- What should be improved next?

## 6. Ready-to-use Evaluation chapter draft

Use this as a working draft. Replace bracketed placeholders with your real values.

---

# Chapter 5: Evaluation

## 5.1 Evaluation Overview

This chapter evaluates Alfred against the three research questions defined in Chapter 1. The evaluation was divided into two parts: verification and validation. Verification focused on whether the system behaved correctly at a technical level, especially when handling real-time financial data. Validation focused on whether the system was useful for its intended users, namely novice and expert cryptocurrency users.

This distinction is important because Alfred is not only a software artifact but also a user-facing assistant. A technically correct system is still weak if its explanations are unclear, while a friendly interface is still unsafe if it generates incorrect financial data. For this reason, Alfred was evaluated on four criteria: routing correctness, factual accuracy, response latency, and user-perceived usefulness.

The verification stage used controlled prompts and ground-truth comparisons against API outputs. The validation stage used a small user study with two groups and a 5-point Likert-scale questionnaire. Together, these methods provide both quantitative and qualitative evidence for the strengths and limits of the current implementation.

## 5.2 Verification

## 5.2.1 Intent Routing Correctness

The first verification task was to check whether the Regex-based intent parser correctly classified user queries before any API call or LLM generation occurred. This was important because Alfred depends on deterministic routing. If the intent parser fails, the rest of the pipeline may call the wrong data source or produce a misleading answer.

To test this, a dataset of [N] prompts was prepared. These prompts covered three intent classes: price queries, TVL or DeFi queries, and general chat. The dataset also included phrasing variations such as full names ("Ethereum"), tickers ("ETH"), abbreviated commands ("btc price"), and more natural sentences ("Can you show me the TVL of Aave right now?"). A small set of edge cases was also included, such as obscure assets, missing entities, and mixed phrasing.

For each prompt, the expected intent and entity were written manually before testing. Alfred's output from `determine_intent()` was then compared against the expected label. The result was an intent classification accuracy of [X]%. Entity extraction accuracy was [Y]%. Most failures occurred in prompts that used uncommon shorthand or referred to assets with ambiguous names.

These results support the decision to use Regex routing for the current project scope. The method is fast, transparent, and easy to debug. It also aligns with the project's aim of reducing hallucination risk by limiting the LLM's role. However, the parser remains brittle when user phrasing falls outside the predefined patterns. This is a known trade-off and an area for future refinement.

## 5.2.2 Ground-Truth Comparison for Numerical Accuracy

The most important technical requirement of Alfred was to avoid financial hallucination when presenting numerical data. To evaluate this, Alfred's generated responses were compared against the exact API values retrieved during the same request. This test focused on the two main data families used in the project: price data from CoinGecko and TVL data from DefiLlama.

The test set contained [N] prompts. Examples included "What is the price of Bitcoin?", "How much is Solana worth?", and "What is the TVL of Curve?". For each prompt, the system recorded:

- the raw API response
- the structured JSON passed into the prompt
- the final LLM output shown to the user

The numerical values in the final response were then checked against the raw API values. For Pro Mode, the expectation was exact reproduction of the values apart from formatting symbols such as commas or currency signs. For Simple Mode, small rounding differences were allowed because that mode is designed to improve readability for novices.

Across the test set, Alfred achieved a numerical mismatch rate of [X]%. In Pro Mode, [A/B] responses matched the API source exactly. In Simple Mode, [C/D] responses remained faithful to the source data after rounding was taken into account. No case was found where Alfred invented an unsupported price or TVL figure. This suggests that the architecture successfully constrained the model to summarise injected data rather than generate unsupported numerical claims.

It is important, however, to define the scope of this claim carefully. The result does not prove that Alfred can never hallucinate under all conditions. It only shows that, within the tested prompt set and system configuration, the combination of deterministic routing, live API retrieval, and strict prompt instructions greatly reduced the chance of numerical hallucination.

## 5.2.3 Latency Testing

The third verification task examined whether the locally hosted architecture could meet the project's latency target of under 10 seconds per query. This was relevant to Research Question 3, which asked whether a local Ollama-based reasoning engine was practical for a conversational crypto assistant.

Latency was measured across [N] runs using the Python `time` module. Each request was divided into three stages:

1. intent parsing
2. external data retrieval
3. local LLM generation

This breakdown was useful because it showed where delays actually occurred. The Regex parser completed in negligible time, usually under [X] ms. The API aggregation stage averaged [Y] seconds. The LLM generation stage was the slowest component, averaging [Z] seconds. The total end-to-end response time averaged [T] seconds, with a maximum recorded value of [M] seconds.

These results show that the project met its practical latency target in most normal cases. The use of `ThreadPoolExecutor` improved performance by allowing CoinGecko and DefiLlama to be queried at the same time rather than sequentially. Without concurrent requests, the system would have had noticeably worse response times.

The findings also show that the main performance bottleneck is not routing or API retrieval, but local model generation. This is an important result because it suggests future optimisation should focus on prompt length, model size, and response formatting rather than replacing the parser or aggregation logic.

## 5.2.4 Edge Cases and Failure Handling

A smaller set of edge-case tests was carried out to examine how Alfred behaved when the input or data source was imperfect. These tests included unknown assets, protocols without available TVL, invalid empty messages, and failed direct ID matching.

The system handled empty messages correctly by returning a client-side error instead of attempting generation. When a direct asset match failed, Alfred attempted a search-based fallback for CoinGecko IDs. This improved robustness for queries such as abbreviated names and lesser-known assets. For assets where TVL was not meaningful or not available, the current implementation returned a placeholder value rather than inventing one.

Although these behaviours are acceptable for a prototype, they also reveal areas for improvement. In particular, displaying "$0" for non-applicable TVL values may mislead users into thinking the metric is genuinely zero. A better approach would be to show "N/A" with a short explanation. This would improve both technical correctness and user trust.

## 5.3 Validation

## 5.3.1 User Study Design

Validation focused on whether Alfred's two-mode interface matched the needs of its target users. A small user study was conducted with two groups:

- Group A: novice users with little or no cryptocurrency background
- Group B: experienced users who were familiar with crypto markets and metrics

Each participant was asked to complete a short task set using Alfred. Novice users were asked questions such as "What is TVL?" and "What is the price of Bitcoin?" in Simple Mode. Expert users were asked to retrieve more detailed information, such as price, market movement, and TVL in Pro Mode. After using the system, participants completed a short questionnaire using a 5-point Likert scale.

The questionnaire measured:

- clarity of the response
- ease of understanding
- perceived usefulness
- trust in the information shown
- suitability of the mode for the user's level

Participants were also invited to leave short comments on what they found confusing or useful.

## 5.3.2 Validation Results

The novice group reported an average clarity score of [X/5] and an average understanding score of [Y/5]. Most participants responded positively to the shorter, analogy-based explanations in Simple Mode. Comments suggested that the system was easier to follow than a raw dashboard because it explained what the numbers meant rather than only displaying them.

The expert group reported an average usefulness score of [X/5] and an efficiency score of [Y/5]. Participants generally preferred the direct, compact formatting of Pro Mode, especially when numerical values were displayed in a structured way. However, some expert users indicated that the system could be improved further by showing more metrics in one response or by adding clearer source timestamps.

Overall, the validation results suggest that the Simple/Pro split was a successful design choice. The same underlying data could be presented in different ways without changing the factual source. This supports the argument that Alfred reduces the barrier to entry for novices while remaining useful to more experienced users.

## 5.3.3 Discussion of Research Questions

The evaluation provides provisional answers to the three research questions.

For Research Question 1, the results indicate that Alfred can prioritise live API data over static model knowledge when answering supported price and TVL queries. Within the tested dataset, the system avoided unsupported numerical generation by grounding the response in retrieved data.

For Research Question 2, the user study suggests that the Simple/Pro mode improves usability for different user groups. Novices benefited from simplified language and analogies, while experts preferred structured and data-dense responses.

For Research Question 3, the latency measurements show that a local Ollama-based architecture is feasible for this use case. Although the model stage remains the slowest part of the pipeline, the overall system stayed within the project's target range in normal use.

## 5.4 Limitations

This evaluation has several limitations. First, the test dataset was relatively small and focused on the project's supported intents. Second, the user study sample size was limited, so the validation results should be interpreted as indicative rather than definitive. Third, external APIs may change over time, which can affect both availability and response format. Finally, the evaluation focused on supported metrics such as price and TVL rather than the full range of possible crypto questions.

These limitations do not invalidate the findings, but they do set the scope of the conclusions. Alfred currently performs best as a constrained educational and market-information assistant rather than a general-purpose financial chatbot.

## 5.5 Summary

In summary, the evaluation shows that Alfred is effective within the boundaries it was designed for. The system demonstrated strong routing transparency, high numerical faithfulness to external data, acceptable response times for a local setup, and useful differentiation between novice and expert modes. At the same time, the tests also revealed improvement areas, especially in edge-case handling, interface polish, and the scale of user testing. These findings provide a clear direction for final refinement and future work.

---

## 7. Ready-to-use Conclusion chapter draft

Use this as a starting point and tune it once your final testing is complete.

---

# Chapter 6: Conclusion

This project set out to build Alfred, a local AI companion for cryptocurrency users that reduces hallucination risk by combining deterministic intent routing, live API aggregation, and a locally hosted large language model. The project addressed three core problems identified in the literature: misinformation in crypto markets, fragmented access to market data, and the difficulty novice users face when trying to understand technical financial language.

The final system demonstrates that a constrained Agentic RAG architecture is a practical solution for this domain. Instead of allowing the language model to answer freely from pre-trained knowledge, Alfred first determines the user intent, retrieves live data from trusted sources, and only then asks the model to translate that data into a readable response. This design choice was central to the project because it shifted the role of the LLM from unsupported generator to controlled summariser.

Another important outcome of the project was the introduction of Simple and Pro modes. This allowed the same underlying data to be adapted for two different audiences. For novice users, Alfred aimed to lower the barrier to entry by using shorter explanations and analogies. For experienced users, Alfred provided a more direct and data-focused response style. The evaluation suggests that this split was useful and aligned well with the needs of both groups.

The project also showed that a local Ollama-based setup is feasible for a university-scale prototype. Although local inference is slower than a cloud-based hosted model, the measured latency remained within an acceptable range for conversational market queries. This supports the ethical and technical rationale for local deployment, especially where privacy and transparency are important.

At the same time, Alfred still has limitations. The intent parser only supports a defined set of patterns and can fail on unusual phrasing. The evaluation sample was small, so the user-study findings should not be treated as universal. The system also depends on third-party APIs, which means availability and schema changes remain an operational risk. Most importantly, Alfred is an informational assistant, not a trading agent, and it should not be used to provide direct financial advice or execute transactions automatically.

Future work should focus on expanding supported intents, improving edge-case handling, and strengthening the evaluation with a larger user study and a broader test dataset. Other useful extensions would include better source timestamps, clearer "not available" handling for unsupported metrics, and a richer frontend that presents structured data more clearly without increasing cognitive load.

Overall, Alfred met the main aim of the project by showing that a carefully constrained local AI assistant can make cryptocurrency data more accessible while reducing the risk of financial hallucination. The project contributes a practical undergraduate implementation of an Agentic RAG system tailored to a noisy and fast-moving domain, and it provides a strong base for further development beyond the CM3070 module.

---

## 8. Fast fixes to make in the current report

Make these changes before your next full draft:

1. Change the title page from `PRELIMINARY PROJECT REPORT` to `FINAL PROJECT REPORT`.
2. Rename `Feature Prototype` to `Implementation`.
3. Add a full `Evaluation` chapter before the conclusion.
4. Add a `Conclusion` chapter.
5. Move `Appendices` and `References` after the six required chapters.
6. Replace absolute wording like `must achieve 0% hallucination rate` with scoped wording like:
   - `The target of the test was zero numerical mismatch within the defined prompt set.`
7. Fix the appendix prompt labels so Simple and Pro are not reversed.
8. Replace informal phrasing:
   - `fixes three issues`
   - `be robotic`
   - `speaking to a 5 year old`

Suggested replacements:

- `addresses three main issues`
- `use a concise and data-focused tone`
- `explain in plain language for a novice user`

## 9. What to do next

Recommended order:

1. Move your current content into the final template.
2. Rename and expand Chapter 4 into `Implementation`.
3. Add the Evaluation draft from this file.
4. Add the Conclusion draft from this file.
5. Tighten the literature and design chapters to fit the final word budget.
6. Reformat references consistently.

## 10. Best next coding/report task

If we continue from here, the highest-value next step is:

**I rewrite your current Chapter 4 into a proper final-report `Implementation` chapter using your exact Alfred architecture and undergrad-level language.**

That would give you a much cleaner draft foundation before we polish the full report.
