# QA observations

The current offline corpus contains 135 expenses across 30 easy, 40 medium and 65 hard cases. The answer key is independent from the engine's returned decision and includes expected first-question fields and final results after scripted replies. All 135 currently match those checks.

The first run of 108 entries exposed 17 differences. They included ambiguous night counts, internal-client wording, nonalcoholic drinks, missing conditional details, and a cent lost when comparing a rounded average. The engine and question builder were corrected and the corpus was expanded.

The latest live model run covers 20 selected language cases with actual extraction and offline FX and publishing. Eighteen match all scripted checks. The remaining differences are retained in live-memos.md.

- H01 asked for both city and nights in the first message. The script answered only nights because its offline fixture already supplied a high-confidence city. The remaining city gap went to Finance. This tests what happens when the real extractor and fixture disagree about which facts are known.
- H13 treats Columbus Inn as insufficient evidence of the city and asks for its location. The isolated arithmetic fixture assumes that location is known. A business name containing a city can be ambiguous in actual records.
- An earlier live run flagged H63 because the model had no explicit vendor label. After adding an evidence-checked vendor classification, the recorded live run rejects the internal team and named vendor meal as expected.

The four explicitly named customer-plus-employee cases H57 through H60 approve in the live run. H61, with employees only and wine on a Saturday, rejects. H62, with an unnamed customer, asks for the company and approves after the answer. H64, with a named customer and no receipt, asks for the receipt and approves after it is supplied. H65 supplies medium extraction confidence in the offline run and asks for confirmation.

One employee contact is enforced by the pipeline. An insufficient reply can leave the case unresolved and routed to Finance. The simulated no-repeat guarantee therefore describes contact behavior. It does not establish that every employee can provide enough information to finalize a decision.

Questions are deterministic in app/questions.py. There is no LLM prompt for writing them. Each employee draft in employee-questions.md is the actual first question attached to that entry's decision. No email was sent.

Run python -m simulation.replay for reproducible rule and question regression checks. Run python -m simulation.replay --live-memos to observe the configured model again. Model labels and confidence can differ between runs. The saved model attempts and rule traces make those differences reviewable.
