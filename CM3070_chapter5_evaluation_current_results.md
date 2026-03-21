# Chapter 5: Evaluation Update Using Current System Evidence

This file converts the real evidence gathered on **20 March 2026** into report-ready text. It should be used alongside the broader Evaluation draft, not as a replacement for final user-study results.

## 5.1 Current Evaluation Scope

At the current stage of development, Alfred has been evaluated using two system-level verification checks:

1. a latency batch covering six representative prompts
2. a reply-consistency batch checking whether the final answer contained the expected live metric

These tests do not replace the planned novice/expert user validation. Instead, they provide initial technical evidence that the implemented system behaves correctly for the supported query types.

## 5.2 Verification Results

### 5.2.1 Latency Batch

On **20 March 2026**, a six-prompt latency batch was executed using the current Alfred implementation. The prompts covered both `SIMPLE` and `PRO` modes and included price queries, TVL queries, and one definition-style prompt. The results were written to `evaluation_outputs/latency_results.csv`.

Across the six prompts, the average timing values were:

- average parser time: **0.09 ms**
- average data-fetch time: **114.73 ms**
- average LLM/final-generation stage: **1921.37 ms**
- average total response time: **2036.26 ms**

These results suggest that Alfred is comfortably within the project's practical latency target of under 10 seconds for the tested prompt set. The parser added almost no meaningful delay, and the dominant cost remained the generation stage. This is consistent with the project's design assumption that routing should be lightweight and that most latency would come from the local reasoning layer.

An additional observation is that the final-generation stage does not always return the response directly from Ollama. Alfred now includes a safety guard that checks whether the model response still respects the project's constraints. In the latency batch, three prompts returned directly from Ollama and three fell back to Alfred's deterministic formatter. This is not a failure of the architecture. Instead, it shows that the system prioritises factual and ethical constraints over always displaying raw model output.

### 5.2.2 Reply-Consistency Batch

A second verification pass was carried out on **20 March 2026** using five supported market queries. This check focused on whether the final answer shown to the user contained the expected live metric from the retrieved data. The results were written to `evaluation_outputs/consistency_results.csv`.

For this batch, Alfred achieved:

- **5 out of 5** successful checks
- **100%** inclusion of the expected live metric in the final response

In this specific run, all five final outputs were delivered through Alfred's deterministic fallback formatter after the safety guard was applied. This result is still useful for the project because the research aim is not to maximise raw LLM output at all costs. The aim is to reduce hallucination and present correct live data safely. In that sense, the fallback mechanism should be treated as part of the implemented reasoning pipeline rather than as a separate failure case.

The result should still be described carefully. It does not prove that Alfred can never hallucinate under all possible prompts. It only shows that, within the supported prompt set tested here, the final user-facing output remained aligned with the retrieved live metric.

## 5.3 Interpretation of Current Results

The current evidence supports three important claims about Alfred.

First, the system architecture is technically efficient. The Regex router is effectively instantaneous, and the combined retrieval plus response pipeline remains well within a conversational threshold for the tested prompts.

Second, the project's guarded design is working as intended. Alfred does not simply trust the language model blindly. Instead, it uses the model when the answer remains within the required constraints and falls back to a deterministic answer when it does not. This is especially important in a financial domain, where a fluent but unsafe response would be worse than a simpler, controlled one.

Third, the present implementation already gives useful material for Research Question 1 and Research Question 3. It provides early evidence that live data can be prioritised over model memory and that a local Ollama-based pipeline is feasible on the project machine.

## 5.4 What Is Still Missing

Although the current verification evidence is real and useful, the Evaluation chapter is not fully complete yet.

The main missing part is the validation study with novice and expert users. The questionnaire, tables, and chapter structure have already been prepared, but the actual participant responses and summary statistics still need to be collected. Until that is done, the project can only claim technical verification, not full user-centred validation.

It would also strengthen the report to run a larger prompt batch for consistency checking and to include more edge cases, such as unsupported metrics, ambiguous asset names, and missing entities.

## 5.5 Suggested Report Wording

Use or adapt the following paragraph in the main Evaluation chapter:

`Initial system-level verification was conducted on 20 March 2026 using the implemented Alfred prototype. A six-prompt latency batch showed an average total response time of 2036.26 ms, with parser time averaging 0.09 ms, data retrieval averaging 114.73 ms, and the final generation stage averaging 1921.37 ms. A separate five-prompt consistency check showed that the final user-facing output contained the expected live metric in all tested cases. In these tests, Alfred sometimes returned direct Ollama output and sometimes switched to a deterministic fallback when the model response failed the system's safety checks. This behaviour was treated as a design strength rather than a failure, because the project prioritises factual reliability and safe communication over unrestricted model fluency.` 

## 5.6 Honest Conclusion for the Evaluation Chapter

At this stage, the technical side of the evaluation has started to become evidence-based rather than hypothetical. However, the project still needs one more stage of work before the Evaluation chapter can be considered complete: the novice versus expert user study. Once those participant results are collected, Alfred will have both verification and validation evidence, which matches the intended structure of the final report.
