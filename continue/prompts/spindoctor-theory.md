---
name: spindoctor-theory
description: Test a theory with the SpinDoctor simulator (file, pasted text, or 'the theory we discussed')
invokable: true
---

Test the theory I point to below with `spindoctor_test_theory`.

- A file path or @-mentioned file: use `source="file"` with `action="extract"` first.
- Pasted text: `source="text"`.
- "The theory we discussed": summarise it from our conversation (claims, assumptions, variables, a measurable prediction), **show me the summary and wait for my confirmation**, then use `source="chat"` with the confirmed summary and short verbatim excerpts. You can't see anything outside this conversation, and very long chats may already be cut off.

Restate the hypothesis, give a measurable prediction, write the q.* script and machine checks, run it (`action="run"`), and report the verdict (supported / not supported / inconclusive), observed vs predicted numbers, and the TXT/PDF theory report paths. State the limits: classical simulation of an idealised model, shot noise, 298 logical qubits with at most 59 per entangled group.
