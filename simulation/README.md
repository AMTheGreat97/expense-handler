# Expense QA replay

Run from the candidate directory.

```powershell
python -m simulation.replay
python -m simulation.replay --live-memos
```

The offline run processes 135 synthetic expenses through the application's batch and follow-up functions. Easy has 30 cases, medium has 40 and hard has 65. Each level has a JSON batch and a separate answer key. The key specifies the expected initial decision, rationale, required question fields and, where applicable, the employee reply and expected final decision.

The offline model returns declared fact fixtures. EUR uses a fixed 1.08 USD rate and GBP a fixed 1.27 USD rate. The publisher records payloads in memory. No Finance endpoint receives these simulations.

For each case the replay submits only the employee answers that match fields actually offered by the first question. It checks whether a second employee reply would be needed, whether a full answer resolves the case and whether an incomplete reply is routed to Finance. This exercises the question's coverage as well as the decision label.

Read results/easy.md, results/medium.md and results/hard.md for every input, expected answer, actual rule trace, question and resulting versions. results/employee-questions.md contains one draft for each initially employee-routed entry. results/traces.jsonl contains the same evidence as structured records.

The live command runs 20 selected difficult language cases with the configured model. It ignores extraction fixtures and keeps FX and publishing offline. Its separate results/live-memos.md and results/live-memos.jsonl preserve differences, including conservative flags. Passing offline checks demonstrates the policy code for those supplied facts. Live results also depend on the model's reading and confidence.

H57 through H65 cover mixed attendance. H57–H60 explicitly combine employees with a named external customer. H61 has internal employees only. H62 leaves the customer unnamed. H63 identifies a vendor. H64 removes the receipt from an otherwise eligible client claim. H65 supplies medium model confidence to verify the question branch.

The root assumption.txt records proposed policies and implementation choices for the presentation. Hotel averaging remains a candidate assumption awaiting Priya.

Questions are assembled by app/questions.py from the engine's gaps. The application does not call an LLM to write the questions. The extraction prompt is app/prompts/system_v1.txt with the applicable category prompt inserted, plus the tagged expense text built in app/extract.py.
