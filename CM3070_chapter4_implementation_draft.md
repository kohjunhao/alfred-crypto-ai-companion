# Chapter 4: Implementation

## 4.1 Chapter Overview

This chapter explains how Alfred was implemented as a working software system. The aim of the implementation was not to build a general-purpose chatbot, but to build a constrained cryptocurrency assistant that could answer a small set of high-value questions using live data. For this reason, the system was designed around four simple modules: a Flask controller, a Regex-based intent parser, a concurrent data aggregation layer, and a local LLM inference engine.

The implementation follows the design choices discussed in Chapter 3. In particular, three technical decisions shaped the final system. First, Alfred uses deterministic routing instead of allowing the language model to decide which tool to call. Second, it retrieves market data from external APIs at query time rather than relying on the model's training data. Third, it changes the response style through prompt engineering so that the same factual data can be presented to either a novice or an expert user. These decisions were made to keep the system transparent, reduce financial hallucination, and maintain acceptable latency on local hardware.

## 4.2 Overall Software Structure

The implemented system is divided into four main Python modules:

- `routes.py`
- `intent_parser.py`
- `data_fetcher.py`
- `llm_engine.py`

The `routes.py` file acts as the entry point of the backend. It receives requests from the frontend, validates the JSON payload, and coordinates the rest of the pipeline. The `intent_parser.py` module handles intent detection and entity extraction using Regular Expressions and a stop-word filter. The `data_fetcher.py` module retrieves live market data from CoinGecko and DefiLlama. The `llm_engine.py` module then turns the retrieved data into a natural-language response using a local Ollama-hosted Llama 3 model.

This separation of responsibilities was important for maintainability. Each module performs one clear task, which made the project easier to test and debug. It also supports the main academic argument of the project: the most safety-critical part of the system, namely market data retrieval, should remain outside the LLM wherever possible.

## 4.3 Request Handling in `routes.py`

The backend was implemented using Flask because the project required a lightweight web server rather than a full-stack framework. The main endpoint of the system is `/api/chat`, which accepts a `POST` request containing two fields: the user's message and the selected mode (`SIMPLE` or `PRO`).

When a request reaches the endpoint, the backend first validates the input. Empty messages are rejected immediately so that the application does not waste time on invalid processing. This is a small implementation detail, but it improves robustness and prevents unnecessary API calls or LLM inference.

After validation, the route passes the raw user message to the intent parser. If the parser detects that the query is a supported financial request, the route continues to the data retrieval stage. If the message is a general conversational prompt, the request can be routed to a simpler response path instead of market-data retrieval. This keeps the control flow easy to follow and ensures that expensive operations are only used when they are needed.

The route then builds a structured payload that contains:

- the original user question
- the detected intent
- the extracted asset or protocol name
- the retrieved live data
- the active user mode

This payload is passed into the LLM engine. The final response returned by the model is then wrapped in JSON and sent back to the frontend, where it is displayed in the chat interface.

One important benefit of this structure is that the LLM never becomes the controller of the system. It only receives already-prepared context. This makes Alfred easier to audit because the decision about what data to fetch is made by normal Python code, not by hidden model behaviour.

## 4.4 Intent Detection in `intent_parser.py`

The intent parser is one of the most important parts of Alfred because it acts as the router for the whole system. Rather than using a machine-learning classifier, the parser uses simple Regular Expressions and keyword filtering. This choice was deliberate. The project only needed to support a small number of intents, so a lightweight rule-based solution was more appropriate than introducing a heavier NLP pipeline.

The parser first normalises the input by converting it to lowercase and removing punctuation. This reduces variation in user phrasing and makes matching easier. It then searches for DeFi-related terms such as `tvl`, `locked`, `yield`, `apy`, and `defi`. If one of these terms is found, the message is classified as a DeFi statistics request. If no DeFi term is found, the parser searches for price-related terms such as `price`, `value`, `cost`, `worth`, and `usd`. Messages that do not match either group can be treated as general chat.

Entity extraction is handled by tokenising the message and filtering out common stop words such as `what`, `is`, `the`, `of`, and `check`. The remaining token or tokens are treated as the likely asset or protocol name. For example, in the query "What is the price of Solana?", the parser removes the filler words and isolates `solana` as the entity. In "Check TVL of Curve", it isolates `curve`.

This approach has two main advantages. First, it is fast. The parser only performs string cleaning and pattern matching, so its latency is negligible compared with network and model inference time. Second, it is transparent. If the parser fails on an edge case, the developer can inspect and update the rules directly. This makes it better aligned with the project's safety goal than a probabilistic classifier whose behaviour would be harder to explain.

The main limitation is that Regex rules can be brittle when users phrase questions in unexpected ways. However, for an undergraduate project with a clearly defined scope, the trade-off is reasonable. The parser is simple enough to justify, yet still effective for the main supported queries.

## 4.5 Live Data Retrieval in `data_fetcher.py`

Once the user intent and entity have been identified, Alfred retrieves live data from external APIs. This happens inside `data_fetcher.py`, which acts as the retrieval layer of the system. Two sources were used:

- CoinGecko, for market data such as price, 24-hour change, market capitalisation, and trading volume
- DefiLlama, for DeFi-oriented metrics such as Total Value Locked (TVL)

The implementation goal was to combine these data sources into a single structured object that could be passed into the language model. Instead of returning data in the format used by each API, Alfred normalises the results into a cleaner dictionary. A combined response may include fields such as asset name, symbol, price in USD, 24-hour change, market cap, volume, FDV, and TVL. This gives the LLM a consistent input format even though the original APIs are different.

To reduce waiting time, Alfred uses `ThreadPoolExecutor` from Python's `concurrent.futures` library. Rather than calling CoinGecko first and DefiLlama second, both requests are submitted at the same time. The backend then waits for the results and merges them into one object. This is an important implementation detail because the system's latency target was under 10 seconds. Since API calls are I/O-bound rather than CPU-bound, threading is a simple and suitable solution here.

The data fetcher also includes a fallback strategy for cases where the user input does not directly match a CoinGecko asset identifier. For example, a user may type a ticker symbol or a partial asset name instead of the full API ID. In such cases, the system can use a search step to find the closest match before requesting the full market data. This improves usability without changing the overall architecture.

Error handling is also important in this layer. External APIs may fail, time out, or return incomplete data. Alfred therefore needs to handle missing fields safely rather than passing invalid values into the LLM. This is especially important in a financial context, because an invented or incorrectly defaulted value can mislead the user. Where data is unavailable, the safer behaviour is to return a null-like placeholder such as `N/A` instead of forcing a number.

## 4.6 Prompt-Guided Response Generation in `llm_engine.py`

After the live market data has been retrieved, the final step is to convert it into a user-facing answer. This is handled by `llm_engine.py`, which communicates with a local Ollama instance running Llama 3.

The most important implementation choice in this module is that the model is treated as a summariser, not as a source of truth. The prompt sent to the model includes the live data retrieved by `data_fetcher.py`, along with a mode-specific system instruction. The model is therefore asked to explain or format the provided data rather than invent its own facts.

Two prompt modes were implemented:

- `SIMPLE`
- `PRO`

The `SIMPLE` prompt asks the model to explain the data in plain language for a novice user. It encourages short responses, limited jargon, and rounded figures where appropriate for readability. The `PRO` prompt asks the model to produce a more direct and technical response, including a structured table and concise commentary. The underlying market data remains the same in both cases. Only the presentation layer changes.

This design directly supports the second research question of the project. The system does not need two different models or two different retrieval pipelines. Instead, it uses one factual input and adapts the wording to the target user group. This keeps the implementation simple while still supporting two distinct user experiences.

The prompt assembly process typically includes:

- the active system prompt
- the user's original question
- the structured real-time data block
- an instruction telling Alfred to answer only from the provided context

This prompt structure constrains the model and reduces the chance that it will fall back on stale training knowledge. Although prompt engineering cannot guarantee perfect behaviour in every possible case, it works well as part of the broader architecture because the most important facts are already determined before the model is called.

## 4.7 Response Guardrail and Safe Fallback

During implementation, an additional safeguard was added between the LLM and the final user output. This was necessary because a local model can still produce wording that does not fit the project's safety goals, even when the correct live data has been supplied. For example, a response may omit the key numerical value, replace it with `N/A`, or drift into advice-like wording.

To address this, Alfred checks the generated response before returning it to the user. If the response does not contain the required live metric, or if it contains wording that conflicts with the system rules, Alfred falls back to a deterministic template response. This means the model is only used when its answer remains aligned with the project's factual and ethical constraints.

This guardrail is important for two reasons. First, it reduces the chance that Alfred will present an unsafe or misleading answer in a financial context. Second, it strengthens the project's claim that the LLM is not treated as an unrestricted authority. Instead, it operates inside a controlled pipeline with a final validation step.

## 4.8 Frontend Integration

The frontend was built with HTML and Tailwind CSS and serves as the interaction layer for the user. From an implementation perspective, the frontend has two important jobs. First, it collects the user's question and sends it to the Flask backend asynchronously. Second, it allows the user to select between Simple and Pro modes before submitting the request.

The selected mode is included in the request payload so that the backend can choose the correct system prompt. This means that mode switching is not just a visual change. It directly changes the prompt logic inside `llm_engine.py`.

The interface also needs to display responses clearly and handle waiting states while Alfred is fetching data and generating an answer. This is especially important in a local-LLM system, because generation may take several seconds. A simple loading state helps the user understand that the query is being processed rather than assuming that the application has frozen.

## 4.9 Implementation Outcomes

The final implementation demonstrates that Alfred can support the core project workflow:

1. receive a user query
2. classify the query using Regex rules
3. extract the asset or protocol name
4. retrieve live data from one or more APIs
5. inject that data into a local LLM prompt
6. return a mode-specific explanation to the user

This workflow is significant because it shows that a local AI assistant can be built without giving the language model full control over retrieval or decision-making. The architecture remains simple enough for an undergraduate project, but still addresses a real problem in a noisy domain.

The implementation also supports the ethical direction of the project. Alfred does not execute trades, manage wallets, or generate direct buy and sell recommendations. Instead, it provides grounded information in a controlled way. This keeps the system aligned with its intended role as an educational and informational companion rather than an automated financial actor.

## 4.10 Current Limitations of the Implementation

Although the current system is functional, several limitations remain. First, the intent parser only supports a limited set of query patterns. Second, the quality of the output still depends partly on prompt wording, which means that the LLM can sometimes respond in a slightly different style than intended. Third, the system depends on third-party APIs, so it can only be as reliable as the availability and format stability of those services.

Another limitation is that the supported data types are still narrow. Alfred currently focuses on price and TVL-related questions rather than a full set of portfolio, on-chain, or risk metrics. This is acceptable for the project scope, but it means the assistant should be described accurately as a focused crypto information assistant rather than a complete market terminal.

Despite these limitations, the implementation succeeded in delivering the core technical artifact of the project: a working Agentic RAG chatbot that uses deterministic routing, live market retrieval, and a local LLM to reduce hallucination risk in cryptocurrency queries.
