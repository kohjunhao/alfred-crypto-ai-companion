# CM3070 Ethics and Deployment Notes

Use this material in the final report, mainly in the Design, Evaluation, and Conclusion chapters.

## 1. Local deployment note for the report

On **19 March 2026**, Alfred was configured to run with a local LLM using Ollama on the project machine. The following components were installed:

- **Ollama 0.18.2**
- **Model:** `llama3:latest`
- **Model family:** Llama 3
- **Parameter size:** 8.0B
- **Quantization:** Q4_0

The model was hosted locally and Alfred accessed it through the Ollama API at `http://localhost:11434`.

Suggested sentence for the report:

`For the final implementation, Alfred was configured to use a locally hosted Llama 3 model via Ollama 0.18.2. The specific model used was llama3:latest (8B, Q4_0 quantisation), running on the project machine and accessed through the local Ollama API.`

## 2. Is local Ollama the best choice for this project?

For this project, local Ollama is a strong choice because it supports the system's two most important non-functional goals: privacy and transparency. Since Alfred is designed as a cryptocurrency assistant, local deployment avoids sending user prompts and market queries to a third-party cloud provider. This fits the ethical stance of the project and strengthens the argument that sensitive financial queries should remain under local control where possible.

At the same time, local deployment introduces a practical trade-off. Other users cannot use the full LLM-backed version unless they also have Ollama and the required model installed on their own machine. For that reason, Alfred was implemented with a fallback response path. This means the product still works without Ollama, but the full project version used for testing and demonstration runs locally with the model installed.

Suggested sentence for the report:

`Although a local LLM reduces portability compared to a hosted cloud service, it was still the better fit for this project because it aligns with the system's privacy goals and keeps the reasoning layer auditable. To reduce the usability impact of local-only deployment, Alfred also includes a safe fallback mode when Ollama is not available.`

## 3. Most important ethical aspects in software design and development

These are the main ethical issues that matter most in a software project like Alfred:

1. **Privacy and data handling**
   - Systems should protect user data and avoid unnecessary disclosure to third parties.

2. **Accuracy and harm prevention**
   - If software presents information that could affect decisions, especially financial or medical decisions, it should reduce the chance of misleading outputs.

3. **Transparency and explainability**
   - Users should be able to understand where information comes from and what the system can and cannot do.

4. **User autonomy**
   - The software should support informed decisions rather than remove user control in high-risk situations.

5. **Fairness and accessibility**
   - The interface and language should not exclude people who are less technical or less experienced.

6. **Security and misuse prevention**
   - The system should reduce the chance of abuse, dangerous automation, or harmful unintended use.

7. **Honest representation of system capability**
   - The project should not claim certainty, intelligence, or safety beyond what has actually been demonstrated.

## 4. Ethical considerations you already took into account in Alfred

These are the strongest ethical points already present in your project:

### 4.1 Data privacy through local inference

By using Ollama locally, Alfred avoids sending user questions to an external LLM provider by default. This is especially relevant because user prompts may reflect financial interests, portfolio concerns, or sensitive behavioural patterns.

### 4.2 Reduction of financial hallucination

The core architecture was designed to reduce unsupported numerical generation. Alfred does not rely on model memory for live prices or TVL. Instead, it retrieves data from external APIs first and only then asks the model to explain the retrieved values. This is an ethical design choice because it attempts to reduce the risk of misleading users in a financial context.

### 4.3 Refusal to provide direct financial advice

Alfred is framed as an informational assistant rather than an autonomous advisor. It does not tell users what to buy or sell, and it does not claim to know future market direction with certainty.

### 4.4 No automated execution of trades

The project deliberately avoids wallet connectivity, order placement, swaps, and automated transactions. This protects user autonomy and reduces the risk of real financial harm caused by misunderstanding or model failure.

### 4.5 Accessibility for different user groups

The Simple/Pro mode design is not only a UX feature but also an ethical choice. It attempts to reduce exclusion by giving novice users explanations they can understand while still preserving utility for more experienced users.

### 4.6 Transparency of sources and architecture

Alfred uses named external sources such as CoinGecko and DefiLlama, and its routing logic can be audited. This is more transparent than a black-box chatbot that provides answers without showing where they came from.

### 4.7 Safe fallback when model output is unsuitable

The final implementation does not blindly trust the local LLM output. Alfred checks whether the generated answer still contains the required live metric and avoids certain advice-like wording. If the response is unsuitable, the system switches to a deterministic fallback response. This is an ethical design choice because it prioritises user safety over model fluency.

## 5. Other ethical considerations you could mention

These are additional ethical considerations that you could reasonably mention in the report, even if you chose not to fully solve them in this version.

### 5.1 API source reliability

Even though Alfred reduces hallucination by using live APIs, those APIs are still external services and may contain missing, delayed, or inconsistent data. You can mention that the system improves trust relative to unsupported model memory, but it still depends on third-party data providers.

### 5.2 Over-trust and interface authority

A clean institutional interface can make a system look more authoritative than it really is. This matters for Alfred because users may place too much confidence in neatly formatted outputs. The project partly addresses this by including non-advice language, but it is still worth acknowledging.

### 5.3 Unequal access to local hardware

Local LLM deployment is ethically attractive for privacy, but it assumes the user has suitable hardware. This means the strongest version of Alfred may not be equally accessible to all users.

### 5.4 Limited evaluation sample size

If your user testing uses a small group of novice and expert participants, you should acknowledge that the system has only been validated on a limited scale. That is an ethical issue of honest reporting rather than a design flaw.

### 5.5 Unsupported queries outside project scope

Alfred only supports a constrained subset of crypto questions. There is an ethical risk if users assume it can answer broader questions about regulation, taxation, portfolio strategy, or security. You can address this by stating the project scope clearly.

## 6. Ethical considerations you could have taken further, but reasonably did not

You asked whether there are other ethical considerations you should have taken into account but decided not to. Yes, there are a few, and it is completely fine to say so in the report if you explain why.

### 6.1 Full user authentication and private data storage controls

You could have added accounts, encrypted chat history, and role-based access control. However, this would have expanded the project into a larger web-platform engineering task and moved it away from the main research aim, which was reducing hallucination and improving accessibility.

### 6.2 Large-scale bias and demographic fairness testing

A broader fairness study across many user backgrounds would be valuable, but it is outside the realistic scope of a single undergraduate project. A smaller novice/expert validation is more appropriate and still aligns with your core research question.

### 6.3 Regulatory compliance features

You could have built more detailed disclaimers, jurisdiction-specific warnings, or compliance rules for financial services. However, Alfred is not positioned as a regulated trading platform, and implementing those features fully would be disproportionate to the project's educational prototype scope.

### 6.4 Multi-provider data verification

It would be ideal to cross-check every metric across several data providers. However, that would add substantial complexity and API management overhead. For this project, using reputable aggregators and clearly stating their limitations is a reasonable compromise.

Suggested sentence for the report:

`Several broader ethical issues, such as full compliance handling, large-scale fairness testing, and multi-provider data verification, were considered but not implemented in this version because they would have expanded the project beyond the scope of an undergraduate prototype. Instead, the project focused on the most relevant ethical risks for this domain: privacy, hallucination reduction, transparency, and the avoidance of direct financial advice or automated execution.`

## 7. Honest status of the report right now

Here is the accurate answer to your question about what is already done in the report materials created so far.

### Already drafted

- Introduction
- Literature Review
- Project Design
- Implementation
- Evaluation chapter structure and draft text
- Conclusion
- Evaluation tables and survey questions
- Ethics and deployment notes

### Partly done but not yet finalised with real evidence

- Latency testing section
- Subject testing section for novice vs expert users
- Numerical verification results
- Final evaluation discussion

These sections exist in draft form, but they still need your actual results inserted.

### Not yet fully produced as finished evidence

- A visual Gantt chart image or polished table
- Real participant responses and summary statistics
- Final latency measurements collected from repeated runs
- Final references clean-up in one citation style

## 8. Best way to phrase the current report status

Suggested sentence:

`The report structure and draft content for all major chapters have been prepared, including literature review, design, implementation, evaluation, and conclusion. However, some parts of the final evaluation, including latency measurements, novice/expert user-study results, and the final project plan visual, still require the insertion of completed empirical evidence from the finished system.`
