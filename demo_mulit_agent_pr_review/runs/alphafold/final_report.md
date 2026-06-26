# AlphaFold Paper-to-PR Title Report

Run: `alphafold`
Paper: Highly accurate protein structure prediction with AlphaFold
Target audience: general science readers
Style: plain press office copy
Round limit: 10 PR Writer versions
Status: approved in 6 PR Writer versions

## Source Availability

Primary source used: Nature open-access article, DOI `10.1038/s41586-021-03819-2`.

Source URL: https://www.nature.com/articles/s41586-021-03819-2

arXiv status: I did not find an arXiv version of this exact Nature paper. The demo uses the freely available Nature open-access article instead.

Statistic used: median CASP14 GDT score of 92.4. In this demo, the Scientist rejects wording that frames 92.4 as generic percent accuracy.

## Final Approved Title

AlphaFold Scores 92.4 on CASP14, Bringing Protein Structures Into Focus

## Agent Iteration Record

### Version 1: Initial Draft

PR Writer title: AlphaFold Uses AI to Solve Protein Folding

Memory: none.

### Scientist Phase

Scientist rejects: "Solve Protein Folding" overstates the paper. The title should say protein structure prediction, not all protein folding or protein biology.

PR Writer revision from Scientist only: AlphaFold **Predicts Protein Structures with High Accuracy**

Scientist approves the accurate version.

Memory added:
- Do not say AlphaFold solves protein folding.
- Keep the claim about protein structures, not all protein biology.

### Marketer Phase

Marketer rejects: the accurate title is dull and lacks a concrete number. The Marketer says a statistic is non-negotiable and proposes: "AlphaFold Hits 92.4% Accuracy and Cracks Protein Folding."

PR Writer revision from Marketer only: AlphaFold **Brings Protein Structures Into Focus with 92.4% Accuracy**

Marketer approves for appeal.

Memory added:
- The title needs a number or statistic for appeal.
- Use the 92.4 result without returning to "solves protein folding."

### Scientist Recheck

Scientist rejects: "92.4% Accuracy" is misleading. The paper reports a median CASP14 GDT score of 92.4, not a generic percent accuracy.

PR Writer revision from Scientist only: AlphaFold Brings Protein Structures Into Focus with a **92.4 CASP14 Score**

Scientist approves the corrected statistic label.

Memory added:
- Do not call the 92.4 result percent accuracy.
- Label 92.4 as a CASP14 score or benchmark score.

### Marketer Recheck

Marketer rejects: the corrected statistic is accurate, but it lands at the end like a technical footnote. The number should drive the title.

PR Writer revision from Marketer only: AlphaFold **Scores 92.4 as AI** Brings Protein Structures Into Focus

Marketer approves the prominent-number version.

### Scientist Final Recheck

Scientist rejects: "Scores 92.4" still needs a compact benchmark label.

PR Writer revision from Scientist only: AlphaFold Scores 92.4 **on CASP14**, Bringing Protein Structures Into Focus

Scientist approves. Marketer rechecks and also approves.

## Title Evolution

| Version | Active Reviewer | Previous Title | New Title | Changed Words | Memory Used |
| --- | --- | --- | --- | --- | --- |
| 1 | none | none | AlphaFold Uses AI to Solve Protein Folding | Initial draft | none |
| 2 | Scientist | AlphaFold Uses AI to Solve Protein Folding | AlphaFold Predicts Protein Structures with High Accuracy | Predicts Protein Structures with High Accuracy | Do not say solves protein folding |
| 3 | Marketer | AlphaFold Predicts Protein Structures with High Accuracy | AlphaFold Brings Protein Structures Into Focus with 92.4% Accuracy | Brings Protein Structures Into Focus with 92.4% Accuracy | Keep protein-structure boundary; add statistic |
| 4 | Scientist | AlphaFold Brings Protein Structures Into Focus with 92.4% Accuracy | AlphaFold Brings Protein Structures Into Focus with a 92.4 CASP14 Score | 92.4 CASP14 Score | Do not call 92.4 percent accuracy |
| 5 | Marketer | AlphaFold Brings Protein Structures Into Focus with a 92.4 CASP14 Score | AlphaFold Scores 92.4 as AI Brings Protein Structures Into Focus | Scores 92.4 as AI | Make the statistic prominent |
| 6 | Scientist | AlphaFold Scores 92.4 as AI Brings Protein Structures Into Focus | AlphaFold Scores 92.4 on CASP14, Bringing Protein Structures Into Focus | on CASP14 | Attach 92.4 to a benchmark label |

## PR Writer Memory Log

| Point Added | Memory Item | Why It Matters |
| --- | --- | --- |
| Scientist phase | Do not say AlphaFold solves protein folding. | Prevents reintroducing the original overclaim. |
| Scientist phase | Keep the claim about protein structures, not all protein biology. | Keeps the title within the paper's scope. |
| Marketer phase | The title needs a number or statistic for appeal. | Captures the Marketer's non-negotiable preference. |
| Marketer phase | Use 92.4 without returning to solved-problem framing. | Allows the number while preserving accuracy memory. |
| Scientist recheck | Do not call 92.4 percent accuracy. | Corrects the statistic framing. |
| Scientist final recheck | Attach 92.4 to CASP14 or a structure benchmark. | Prevents readers from treating the score as universal. |

## Science-Marketing Tension Log

| Moment | Marketer Pull | Scientist Boundary | Resolution |
| --- | --- | --- | --- |
| Initial title | Big claim: solve protein folding | Too broad; paper is about protein structure prediction | Scientist phase removes the overclaim |
| First marketing pass | Add 92.4% accuracy and a stronger image | Statistic is not yet checked | Marketer gets a statistic into the title |
| Scientist recheck | Keep 92.4% as catchy shorthand | 92.4 is a CASP14 GDT score, not percent accuracy | PR Writer changes it to 92.4 CASP14 Score |
| Marketer recheck | Move the number forward | Do not lose score framing | PR Writer opens with Scores 92.4 |
| Final science check | Keep the prominent number | Add benchmark context | Final title says Scores 92.4 on CASP14 |


## Artifact Index

| Artifact | Purpose |
| --- | --- |
| `dialogue.jsonl` | Machine-readable turn log |
| `rounds/pr_writer_round_XX.yaml` | PR title versions and memory |
| `rounds/scientist_round_XX.yaml` | Accuracy reviews and statistic checks |
| `rounds/marketer_round_XX.yaml` | Appeal reviews and statistic pressure |
| `papers/alphafold_2021_source_notes.md` | Source availability and paper facts used |
