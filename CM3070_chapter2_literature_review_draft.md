# Chapter 2: Literature Review

## 2.1 Introduction

This chapter reviews the literature relevant to Alfred and uses it to justify the project's design choices. The review focuses on five themes. First, the cryptocurrency market is highly vulnerable to misinformation and sentiment-driven behaviour. Second, market data is fragmented across multiple sources and interfaces. Third, standard Large Language Models are unsuitable for real-time financial questions without access to external tools. Fourth, novice users face a barrier to entry because crypto information is often presented in specialist language. Fifth, existing crypto AI products still leave important gaps in transparency, safety, or accessibility.

Taken together, these themes explain why Alfred is designed as a constrained Agentic RAG assistant rather than a general-purpose chatbot or execution agent.

## 2.2 Vulnerability to Misinformation in Cryptocurrency Markets

Several sources argue that cryptocurrency markets are unusually exposed to misinformation. Unlike traditional finance, crypto markets are not organised around one tightly regulated reporting structure. Information spreads across exchanges, Telegram groups, X, YouTube, Discord, newsletters, and anonymous online accounts. This allows rumours and narrative shifts to influence behaviour very quickly.

Kutle (2021) highlights the vulnerability of the crypto market to false or misleading news, while Raheman et al. (2022) show that social-media sentiment can strongly affect cryptocurrency volatility. Li, Wang and Zhang (2024) similarly argue that price movements in crypto assets can be associated with social-media activity rather than only underlying fundamentals. These studies differ in method and scope, but they point in the same direction: sentiment has outsized power in crypto markets.

This matters for Alfred because it supports the decision not to treat social chatter as the main knowledge source. If a chatbot simply summarises the loudest online narratives, it may reproduce the same misinformation problem it is supposed to solve. Alfred therefore prioritises verifiable market data from established API providers rather than sentiment scraping. The literature does not imply that market data is perfectly objective, but it does suggest that structured metrics are a safer foundation than unfiltered online commentary.

## 2.3 Market Data Fragmentation

A second problem identified in the literature and industry reports is fragmentation. In traditional finance, market participants can often rely on consolidated terminals and well-known data vendors. In crypto, the user may need to move between multiple websites just to answer one simple question. Price data may be found on exchange aggregators, on-chain activity on blockchain explorers, and protocol metrics such as TVL on DeFi dashboards.

This fragmentation increases cognitive load, especially for less experienced users. Even when the data is publicly available, it is not always easy to discover, combine, or interpret. TRM Labs' 2026 Crypto Crime Report also points to the scale and dispersal of modern crypto activity across chains and Layer 2 networks. Although the report is not primarily about user interfaces, it reinforces the broader point that crypto activity is spread across many systems rather than a single unified platform.

The relevance to Alfred is direct. The project treats aggregation as a core function rather than an optional feature. By pulling price-related information from CoinGecko and TVL-related information from DefiLlama, Alfred gives the user a more unified view than either source alone. This is not a complete answer to fragmentation, but it is a practical response within the scope of an undergraduate project.

## 2.4 Knowledge Cut-off and LLM Hallucination

The literature on LLMs makes clear that these models are powerful language tools but weak sources of real-time factual truth. OpenAI documentation (2023) confirms that standard pre-trained models do not automatically know current events or live market conditions unless connected to external tools. In a fast-moving financial environment, this limitation is especially serious.

Sert (2025) discusses factual hallucination in financial contexts, where models can generate numbers that sound plausible but are not grounded in current reality. This type of failure is dangerous because it is often not obvious to the user. A hallucinated price may still look reasonable on first reading, which makes it more risky than an obviously broken answer.

This body of work strongly motivates Alfred's core architecture. In Alfred, the LLM is not asked to remember the current price of Bitcoin or the current TVL of a protocol. Instead, live data is retrieved first, and the model is instructed to work only from that context. This design does not eliminate all possible model failure, but it reduces the scope of the model's job. The model is used to explain and format retrieved data, not to invent unsupported facts.

## 2.5 Barriers to Entry and Crypto Jargon

The crypto industry also presents an accessibility problem. Lewis (2018) shows that cryptocurrency and blockchain concepts are often introduced through specialised terms that assume technical knowledge. Even basic participation may require understanding ideas such as private keys, gas fees, liquidity pools, slippage, staking, or TVL.

This creates a knowledge moat. A user may be able to access the same numbers as an expert, but still lack the context needed to understand them. As a result, many current tools are functionally open but practically inaccessible. A dashboard full of abbreviations and metrics may not help a beginner even if the data is accurate.

This gap motivates Alfred's two-mode design. Instead of building one response style for all users, the project assumes that the same factual input can be made more useful by adapting the language and presentation style. The literature does not prescribe a Simple/Pro split specifically, but it supports the broader idea that accessibility depends not only on what information is shown, but how it is communicated.

## 2.6 Existing Crypto AI Tools

The current market already includes several AI-labelled crypto tools, but the literature and product landscape suggest that they do not fully solve the problem Alfred is addressing. Broadly, these tools can be grouped into three categories: sentiment and narrative agents, execution-focused agents, and natural-language data interfaces.

### 2.6.1 Sentiment and Narrative Agents

Tools such as AIXBT and Elfa.AI focus heavily on social signals, narrative tracking, or private-group monitoring. Their value proposition is speed: they attempt to detect market narratives before the wider market reacts. However, this design has weaknesses. If the source material is noisy or manipulable, then the tool may amplify unreliable signals instead of correcting them. Liu and Tsyvinski (2021) discuss risk and returns in cryptocurrency markets more broadly, and although their work is not about AI products specifically, it reinforces the idea that crypto markets are highly speculative and volatile.

For Alfred, the key lesson is that a crypto assistant should not rely mainly on social sentiment if its aim is to improve trust and reduce misinformation. This is why Alfred avoids making social-signal analysis the centre of its architecture.

### 2.6.2 Execution Agents

Another class of tools focuses on action rather than explanation. Examples include systems that interpret user prompts and then carry out swaps, bridging, or other on-chain operations. These tools can be powerful, but they also introduce risk. If the system misunderstands a command or the user misunderstands the response, the outcome may involve direct financial loss rather than only misinformation.

This is where Alfred takes a different position. The project deliberately stops at information support. It does not execute trades or automate wallet actions. This is both a design choice and an ethical safeguard. For a project aimed partly at novices, education and explanation are more appropriate than autonomous execution.

### 2.6.3 Natural-Language Data Interfaces

A third category includes interfaces such as LlamaAI by DefiLlama, which provide natural-language access to specific datasets. These tools are often more reliable than sentiment agents because they are grounded in structured data. However, they may still be limited in scope. A system focused only on DeFi metrics may not provide broader market context, while a price-focused interface may not explain what a metric means for a beginner.

This gap helps justify Alfred's role as an aggregation and translation layer. Alfred combines data from more than one source and then adapts the output to different users. In this sense, it sits between a raw data terminal and a conversational explainer.

### 2.6.4 The Black-Box Issue

Across all three categories, another issue appears repeatedly: opacity. Many commercial AI tools do not reveal their exact prompts, routing logic, or safety boundaries. In a financial context, this is a serious weakness because users cannot easily judge whether the answer came from live data, stale training data, or unsupported inference.

Alfred responds to this issue by being auditable. The routing rules are written in Python, the data sources are named directly, and the system prompts can be inspected. This does not make the system perfect, but it does make it easier to understand and evaluate.

## 2.7 Agentic RAG as a Design Approach

Retrieval Augmented Generation (RAG) is usually associated with vector databases and semantic search over static documents. In many applications, this works well because the underlying information does not change rapidly. Cryptocurrency data is different. A vector database containing yesterday's market values would not solve the factuality problem for a user asking about the market now.

For this reason, Alfred uses a narrower but more suitable form of Agentic RAG. Instead of retrieving chunks from a document store, the system first determines which external tool should be called, then retrieves live structured data, and finally uses the model to generate the response. The retrieval step is therefore dynamic and tool-driven rather than document-driven.

This design is important for two reasons. First, it matches the time-sensitive nature of the domain. Second, it reduces the burden on the LLM. The model does not need to choose between many ambiguous sources at generation time, because the routing and retrieval decisions have already been made by the backend.

## 2.8 Chain of Thought and Prompt Constraint

Chain of Thought (CoT) prompting is often used to encourage models to reason through a task step by step. In Alfred, the value of prompt design is more practical than theoretical. The prompt tells the model to inspect the supplied data, prioritise that data over any background knowledge, and respond in the style required by the active mode.

It is important not to overstate what CoT can do. Prompting alone does not guarantee accuracy, and it cannot replace live retrieval. However, within Alfred's architecture, prompt constraint still plays an important role. It helps keep the model focused on the injected JSON data and reduces the chance that the model will drift into generic crypto commentary or unsupported claims.

This means CoT-style prompting is useful here as a secondary safeguard rather than the main safety mechanism. The main safeguard is still the architecture itself: deterministic routing plus live retrieval.

## 2.9 Synthesis and Research Gap

The reviewed literature points to a clear gap. Existing studies and products show that:

- crypto markets are noisy and influenced by sentiment
- important data is fragmented across multiple sources
- LLMs cannot be trusted for live financial facts without tool support
- novice users struggle with specialist terminology
- many AI products are opaque, narrow in scope, or oriented toward action rather than explanation

What is missing is a lightweight system that combines these insights into one practical design. Alfred addresses that gap by bringing together four ideas in one undergraduate implementation:

- deterministic intent routing
- live multi-source retrieval
- local LLM inference for privacy and transparency
- dual response modes for different user groups

The literature therefore does more than justify the topic. It directly explains why Alfred is structured in the way it is. The project does not claim to solve all problems in crypto information systems, but it does present a focused response to a real design gap.

## 2.10 Chapter Summary

This chapter has reviewed the main literature areas relevant to Alfred: misinformation, fragmentation, LLM knowledge cut-off, accessibility barriers, existing crypto AI tools, and the relevance of Agentic RAG. The review shows that a simple chatbot trained on static knowledge would be unsuitable for this domain. It also shows that current crypto AI products often sacrifice either transparency, safety, or accessibility. These findings motivate Alfred's design as a constrained, data-grounded, and user-adaptive assistant. The next chapter explains how those ideas were translated into the system architecture and implementation plan.
