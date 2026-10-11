---
name: spindoctor-run
description: Run SpinDoctor q.* commands with the local classical simulator
invokable: true
---

Run the q.* commands I give below with the `spindoctor_run_script` tool (one command per line). Then summarise the results, put the exact probabilities next to the sampled counts, and list the TXT/PDF report paths. Remind me that this is a classical FP64 simulation on my computer, not quantum hardware, and that registers wider than 29 qubits (up to 298) sample in basis z only.
