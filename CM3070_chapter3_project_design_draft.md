# Chapter 3: Project Design

## 3.1 Introduction

This chapter explains how Alfred was designed to address the problems identified in Chapters 1 and 2. The design had to meet two goals at the same time. First, it had to reduce the risk of hallucinated financial data by grounding responses in live external information. Second, it had to present that information in a way that matched the needs of different users. These goals shaped the architecture, the technical stack, the development plan, and the evaluation strategy.

## 3.2 Target Users and Domain

The project sits in the domain of cryptocurrency information support. More specifically, it addresses the problem of helping users retrieve and understand live market data without relying on either noisy social sentiment or a general-purpose chatbot.

Two target user groups were defined during the design stage.

### 3.2.1 Novice User: Simple Mode

The first target group is novice users with little or no experience in cryptocurrency markets. These users may understand basic ideas such as price, but often struggle with metrics such as TVL, FDV, or volume. They may also find standard crypto dashboards too dense or too technical. For this group, Alfred needed to reduce jargon and explain numbers in plain language.

Simple Mode was designed for this purpose. The mode instructs Alfred to keep responses short, use ordinary wording, and explain the significance of the data rather than only listing it. The goal is not to oversimplify the market, but to make the first layer of understanding less intimidating.

### 3.2.2 Experienced User: Pro Mode

The second target group is more experienced users who want fast access to key figures. These users are likely to be familiar with common crypto metrics and do not need long explanations. For them, the value of Alfred lies in speed, structure, and compactness.

Pro Mode was therefore designed to present the same market data in a denser and more direct format. This mode uses more technical language and structured formatting, such as tables, while still remaining grounded in retrieved data.

The choice to support two user groups reflects one of the project's main arguments: the usefulness of financial information depends not only on whether it is accurate, but also on whether it is presented at the right level for the user.

## 3.3 Design Requirements

Based on the project aim and literature review, the following design requirements were established.

### Functional requirements

- The system must accept natural-language user queries through a web interface.
- The system must distinguish between supported financial queries and general chat.
- The system must identify the asset or protocol being requested.
- The system must retrieve live market data from external APIs.
- The system must generate a response using either Simple or Pro mode.
- The system must return the response through the chat interface.

### Non-functional requirements

- The system should reduce hallucination risk by grounding responses in retrieved data.
- The system should remain transparent and easy to inspect.
- The total response time should remain within a practical conversational threshold, set at under 10 seconds where possible.
- The system should preserve user privacy by running the model locally.
- The interface should remain simple enough for a novice user to operate.

These requirements directly shaped the architecture described below.

## 3.4 High-Level Architecture

Alfred was designed as a four-layer system:

1. interface and control layer
2. intent parsing layer
3. data aggregation layer
4. synthesis layer

This separation was chosen so that retrieval and control logic could remain outside the language model. In other words, the system does not ask the LLM what tool to call. It uses Python code for that decision first, then asks the LLM to explain the retrieved output.

### 3.4.1 Interface and Control Layer

The user interacts with Alfred through a simple web interface built with HTML and Tailwind CSS. The frontend sends the user's message and selected mode to a Flask backend. Flask acts as the central controller of the system. It receives the input, validates it, calls the parser, triggers data retrieval when necessary, and returns the final result.

This layer was kept lightweight on purpose. The project did not require a complex full-stack framework, and a simpler backend makes the request flow easier to explain and maintain.

### 3.4.2 Intent Parsing Layer

The intent parser acts as the router for the system. It decides whether a query is asking for market price information, a DeFi-related metric such as TVL, or general conversation. It also extracts the likely asset or protocol name from the query.

This layer is important because it determines which data source should be called next. A query about Bitcoin price should not be handled in the same way as a query about Aave TVL. By using deterministic Regex rules, this layer makes the routing process transparent and efficient.

### 3.4.3 Data Aggregation Layer

Once the intent and entity are known, Alfred retrieves the relevant data from external sources. CoinGecko is used for price-related information such as market price, market cap, volume, and FDV. DefiLlama is used for DeFi-related metrics such as TVL.

The outputs of these APIs are then normalised into a single structured dictionary so that the next layer can work from one clean context object rather than multiple raw responses.

### 3.4.4 Synthesis Layer

The final layer is the local LLM. Alfred uses Ollama to host Llama 3 on the local machine. The model receives a system prompt, the user's question, and the structured live data block. It then generates the final response in either Simple or Pro style.

The model is deliberately placed at the end of the pipeline. This ensures that it does not decide what the facts are. It only transforms retrieved facts into a readable answer.

## 3.5 Data Flow

The end-to-end flow of a typical request is as follows:

1. The user enters a message in the frontend and selects either Simple or Pro mode.
2. The frontend sends a `POST` request to the Flask backend.
3. The backend validates the input.
4. The message is passed to the intent parser.
5. The parser identifies the intent and extracts the entity.
6. The backend calls the relevant data retrieval functions.
7. CoinGecko and DefiLlama are queried concurrently where appropriate.
8. The retrieved data is merged into one structured context object.
9. The backend selects the correct system prompt based on the active mode.
10. The prompt and data are sent to the local LLM.
11. The generated response is returned as JSON and rendered in the chat interface.

This flow is intentionally simple. Each stage has a clear role, and each stage can be tested separately. This supports both implementation and evaluation.

## 3.6 Justification of Key Design Choices

### 3.6.1 Regex Routing Instead of Probabilistic Routing

One of the most important design decisions was to use Regex-based intent detection instead of a heavier machine-learning or LLM-based router. This was chosen for three reasons.

First, the set of supported intents is small. The project only needed to distinguish among a few high-value query types, so a rule-based approach was sufficient. Second, Regex matching is fast, which helps the project meet its latency target. Third, Regex rules are transparent and easy to debug, which is valuable in a financial setting where explainability matters.

The main trade-off is reduced flexibility. A rule-based parser may miss unusual phrasing more easily than a probabilistic classifier. However, within the defined project scope, the gains in transparency and simplicity outweighed that limitation.

### 3.6.2 Live API Retrieval Instead of Static Knowledge

The literature review showed that real-time market data cannot safely be answered from model memory alone. This is why Alfred retrieves data from external APIs at request time. CoinGecko and DefiLlama were selected because they are widely used, publicly accessible, and suitable for the specific metrics needed in the project.

This design directly supports Research Question 1, since it tests whether the model can be constrained to prioritise retrieved facts over pre-trained knowledge.

### 3.6.3 Local LLM Deployment

Running the model locally through Ollama was another deliberate choice. A cloud API may offer lower setup complexity, but local hosting better supports privacy, transparency, and project independence. Since Alfred is intended as a financial assistant, keeping user queries on the local machine is a meaningful ethical and technical advantage.

The trade-off is that local inference may be slower than a hosted service. This is why latency testing forms an important part of the final evaluation.

### 3.6.4 Dual Output Modes

The Simple/Pro design was introduced because the same data is not equally useful to all users in the same form. A novice may need explanation and context, while a more experienced user may want a compact factual summary. Instead of building two systems, Alfred uses one retrieval pipeline and changes only the response instructions.

This keeps the architecture clean while still supporting two user groups. It also makes evaluation easier, because both modes can be compared while controlling for the underlying data.

## 3.7 Technical Stack

The main technologies used in the design are listed below.

### Flask

Flask was chosen as the backend framework because it is lightweight and well suited to a small API-driven application. It handles request routing clearly without adding unnecessary framework complexity.

### Python

Python was selected because it supports fast prototyping, readable backend logic, easy HTTP requests, and straightforward concurrency through the standard library. It was also appropriate for integrating with Ollama and for implementing the intent parser.

### Ollama with Llama 3

Ollama provides a practical way to run a local LLM. Llama 3 was chosen as the reasoning engine because it supports general natural-language generation while remaining usable on local hardware.

### CoinGecko and DefiLlama APIs

These APIs were chosen because together they cover the main data types required for the project. CoinGecko supplies price and market information, while DefiLlama supplies DeFi metrics such as TVL.

### Tailwind CSS

Tailwind CSS was used for the frontend because it allows fast interface iteration and clean styling without needing a large amount of custom CSS.

## 3.8 Development Plan

The project followed an iterative development approach rather than a strict waterfall process. This was appropriate because the design included several components that had to be tested together, especially the parser, the retrieval layer, and the response prompts.

The development work was broken into small stages:

1. establish the project scope and architecture
2. implement the Flask route and basic interface
3. build the Regex-based intent parser
4. integrate CoinGecko and DefiLlama retrieval
5. implement concurrent fetching for latency reduction
6. add Simple and Pro prompt modes
7. test response quality, edge cases, and latency
8. carry out user-centred evaluation and write the final report

A more detailed Gantt chart or schedule can be included in the appendix. In the main text, the important point is that the project was developed incrementally, with each stage producing a working piece of the system.

## 3.9 Evaluation Plan

The design of Alfred was closely linked to its evaluation plan. The project needed to show not only that the software runs, but also that it addresses the three research questions in a measurable way.

Three main evaluation strands were planned.

### 3.9.1 Verification of Routing and Accuracy

The first strand focuses on technical correctness. This includes testing whether the intent parser correctly classifies supported query types and whether the final output remains faithful to the retrieved market data.

### 3.9.2 Validation of User-Facing Modes

The second strand focuses on user usefulness. A small study with novice and experienced users was planned to test whether Simple Mode improves clarity for beginners and whether Pro Mode remains useful for more advanced users.

### 3.9.3 Latency Testing

The third strand focuses on performance. The time taken for parsing, data retrieval, and LLM generation would be measured separately so that bottlenecks could be identified clearly.

This evaluation plan ensures that the final project can be judged on functionality, usefulness, and feasibility rather than on implementation alone.

## 3.10 Chapter Summary

This chapter has described the design of Alfred as a constrained Agentic RAG system built around four layers: interface, routing, retrieval, and synthesis. It has justified the main design decisions, including Regex-based routing, live API retrieval, local LLM deployment, and Simple/Pro response modes. It has also outlined the development and evaluation plans that guide the project. The next chapter explains how this design was implemented in code.
