# Chapter 1: Introduction

## 1.1 Project Context and Motivation

Cryptocurrency markets create an unusual information problem for retail users. In traditional finance, investors usually rely on regulated exchanges, standardised reporting, and established information channels. In contrast, the cryptocurrency market is fragmented across centralised exchanges, decentralised protocols, blockchain explorers, and fast-moving social media platforms. This makes it difficult for users to identify which information is current, which source is trustworthy, and what a given metric actually means.

This problem is especially serious for less experienced users. Many important crypto terms, such as Total Value Locked (TVL), slippage, gas fees, and Fully Diluted Valuation (FDV), are not self-explanatory. A beginner may be able to find a number, but still not understand whether it matters or how to interpret it. At the same time, social platforms often amplify hype, rumours, and misleading narratives. In such an environment, the user does not only face a lack of information, but also an excess of low-quality information.

Large Language Models (LLMs) seem attractive as a solution because they can answer questions in natural language. However, they also introduce a major risk in financial contexts. Standard LLMs are trained on static datasets and therefore suffer from a knowledge cut-off problem. Without access to external tools, they cannot reliably answer time-sensitive questions such as the current price of Bitcoin or the latest TVL of a DeFi protocol. In practice, this can lead to hallucination, where the model generates a plausible but incorrect figure. In a financial setting, even a small numerical error can reduce trust and may influence poor decision-making.

This project addresses that problem through a constrained chatbot called **Alfred: Your Crypto AI Companion**. Alfred is designed as an Agentic Retrieval Augmented Generation (RAG) system that combines a local language model with deterministic routing and live API retrieval. Instead of asking the language model to answer directly from pre-trained knowledge, Alfred first identifies the type of user query, then retrieves the relevant data from trusted external sources, and only then uses the model to explain that data. This architecture reduces the chance of unsupported numerical generation and makes the system easier to inspect.

The project also addresses accessibility. Alfred includes two response modes: **Simple Mode** and **Pro Mode**. Simple Mode is intended for novice users who need short explanations in plain language. Pro Mode is intended for users who prefer compact, data-focused responses. Both modes use the same underlying market data, but present it differently according to the user's needs. This means the project is not only concerned with technical correctness, but also with how effectively financial information can be communicated to different user groups.

The project draws inspiration from the financial assistant template discussed in earlier University of London coursework, but adapts it to a crypto-specific setting. The focus is not on automated trading or portfolio execution. Instead, Alfred is an educational and informational assistant that helps users access live market data more safely and clearly.

## 1.2 Project Aim

The main aim of this project is to design and implement a local cryptocurrency chatbot that reduces financial hallucination by grounding responses in live API data and presenting that data in a form suitable for either novice or expert users.

In practical terms, the project aims to show that a lightweight Agentic RAG architecture can be used to make cryptocurrency information more accessible without giving full control to the LLM. The chatbot should be able to answer a small set of high-value user questions, such as price queries and TVL-related queries, while keeping the system transparent, explainable, and responsive enough for real use.

## 1.3 Research Questions

To guide the implementation and evaluation of Alfred, the project is structured around three research questions:

**RQ1. How can a local LLM-based chatbot prioritise live market data over pre-trained knowledge when answering cryptocurrency queries?**

This question addresses the core technical problem of knowledge cut-off and hallucination. The project investigates whether deterministic routing and prompt-grounded retrieval can reduce unsupported numerical answers.

**RQ2. Does presenting the same market data through Simple and Pro response modes improve usability for users with different levels of cryptocurrency knowledge?**

This question examines the educational and interface value of the system. The goal is to test whether the project can lower the barrier to entry for novices without making the output less useful for more experienced users.

**RQ3. Can a locally hosted architecture using Flask, concurrent API retrieval, and Ollama deliver acceptable latency for real-time cryptocurrency queries?**

This question focuses on feasibility. Even if the system is accurate, it still needs to respond within a practical time window to be useful as a conversational assistant.

## 1.4 Objectives

To answer these research questions, the project is divided into four technical objectives.

The first objective is to build a backend controller that can distinguish between supported market-data queries and ordinary conversational input. This is done through a Regex-based intent parser rather than a machine-learning classifier. The purpose of this design is to keep routing simple, fast, and transparent.

The second objective is to integrate live external data sources into the response pipeline. Alfred retrieves price-related market information from CoinGecko and DeFi-oriented metrics such as TVL from DefiLlama. These sources are combined into one structured data object before the LLM is called.

The third objective is to implement two presentation modes, Simple and Pro, using separate system prompts. The aim is to show that one factual data source can support two different communication styles without changing the underlying truth.

The fourth objective is to evaluate the system using both technical and user-centred methods. Technical evaluation focuses on routing correctness, numerical faithfulness to API outputs, and latency. User-centred evaluation focuses on whether novice and expert users find the two modes clear and useful.

## 1.5 Deliverables

The main deliverable of the project is a working prototype of Alfred as a local web-based chatbot. The prototype includes:

- a Flask backend
- a Regex-based `intent_parser.py` module
- a `data_fetcher.py` module that retrieves live data from CoinGecko and DefiLlama
- an `llm_engine.py` module that queries a local Ollama-hosted Llama 3 model
- a simple frontend with a Simple/Pro mode toggle

The second deliverable is the evaluation of the system. This includes verification tests for supported query types, ground-truth comparison against retrieved market data, latency measurements, and a small user study using 5-point Likert-scale responses.

The third deliverable is the written final report and accompanying presentation material, which document the motivation, literature background, design decisions, implementation approach, evaluation results, and limitations of the project.

## 1.6 Scope and Ethical Position

It is important to define the scope of the project clearly. Alfred is not designed to be a trading bot, an autonomous financial agent, or a portfolio management system. It does not execute transactions, access private wallets, or issue direct buy and sell instructions. Its purpose is narrower: to provide grounded, readable cryptocurrency information using live data.

This limited scope is also an ethical choice. Financial chatbots can create harm if users mistake generated text for professional advice. For this reason, Alfred is designed to avoid direct recommendations and instead focus on explanation and data presentation. The choice to run the model locally through Ollama also supports user privacy, since queries do not need to be sent to a third-party cloud provider for inference.

## 1.7 Chapter Summary

This chapter has introduced the motivation for Alfred and defined the main problem the project aims to solve: the tension between natural-language accessibility and factual reliability in cryptocurrency information systems. It has also set out the research questions, objectives, deliverables, and ethical boundaries of the project. The next chapter reviews the relevant literature on misinformation in crypto markets, knowledge cut-off in LLMs, existing crypto AI tools, and the use of Agentic RAG as a safer design approach.
