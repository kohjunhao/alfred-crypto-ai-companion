# CM3070 Gantt Chart Draft

Use this as the basis for your final project plan visual. You can convert it into a figure or table in the report.

```mermaid
gantt
    title Alfred Project Plan
    dateFormat  YYYY-MM-DD
    axisFormat  %d %b

    section Planning
    Project proposal and topic definition     :done, p1, 2025-10-01, 2025-10-21
    Literature collection and reading         :done, p2, 2025-10-22, 2025-11-20
    Draft literature review                   :done, p3, 2025-11-21, 2025-12-05

    section Design
    Architecture and user-mode design         :done, d1, 2025-11-25, 2025-12-10
    Preliminary report preparation            :done, d2, 2025-12-01, 2025-12-18

    section Implementation
    Flask backend scaffold                    :active, i1, 2026-03-19, 2026-03-22
    Regex intent parser                       :active, i2, 2026-03-19, 2026-03-22
    CoinGecko and DefiLlama integration       :active, i3, 2026-03-20, 2026-03-23
    Ollama integration and prompt tuning      :active, i4, 2026-03-20, 2026-03-24
    Frontend UI and mode switching            :active, i5, 2026-03-20, 2026-03-25

    section Testing and Evaluation
    Unit testing and edge-case checks         :i6, 2026-03-23, 2026-03-26
    Latency measurement runs                  :i7, 2026-03-24, 2026-03-27
    Novice and expert user testing            :i8, 2026-03-24, 2026-03-30
    Evaluation chapter write-up               :i9, 2026-03-27, 2026-03-31

    section Final Submission
    Final report editing                      :f1, 2026-03-28, 2026-04-03
    Demo video recording                      :f2, 2026-03-31, 2026-04-03
    Final checks and submission               :f3, 2026-04-03, 2026-04-05
```

Suggested sentence for the report:

`The project followed an iterative plan in which literature review, architecture design, implementation, and evaluation were developed in overlapping stages rather than as a strict linear waterfall process.`
