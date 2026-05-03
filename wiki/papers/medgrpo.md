# MedGRPO

Last updated: 2026-05-03

## Summary

MedGRPO is a reinforcement learning framework for heterogeneous medical video understanding. Its key claim is that standard RL can collapse when medical video datasets and tasks have incompatible reward scales, and that balanced multi-dataset learning requires reward normalization plus domain-specific caption evaluation.

## Key Points

- The paper introduces MedVidBench, a benchmark with 531,850 video-instruction pairs from 8 medical video sources and 8 task types. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- MedVidBench spans video-level, segment-level, and frame-level tasks, so models must handle procedural summaries, temporal grounding, region captioning, and instrument localization. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- The data pipeline converts existing expert annotations into instruction-following QA pairs using annotation-enriched prompting, dual-model generation, and validation. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- Naive GRPO fails because easy dataset-task pairs produce larger raw rewards than hard pairs, causing optimization to over-focus on easy sources and destabilize learning. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- MedGRPO applies dataset-task-specific logistic reward normalization so each dataset-task median maps to reward 0.5. This creates "median fairness" across heterogeneous tasks. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- For medical captioning, the paper argues that generic semantic similarity misses clinically important errors such as wrong instruments, vague anatomy, inaccurate actions, or weak spatial detail. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- The medical LLM judge scores captions across terminology precision, instrument and anatomy identification, specificity, clinical procedure context, and action/state accuracy. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- On Qwen2.5-VL-7B, MedGRPO improves the SFT baseline on most reported grounding and captioning metrics, while NAP decreases because it is not optimized by the RL reward set. [source](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)

## Practical Takeaways

- For multi-dataset RL, do not assume raw metrics are comparable across datasets or tasks.
- Use a held-out or baseline model to estimate reward percentiles before RL, then normalize rewards per dataset-task pair.
- In clinical domains, evaluate generated text with criteria that reflect domain-specific correctness rather than only semantic closeness.
- Pair grounding tasks with captioning tasks when the domain requires both spatial localization and procedural semantics.

## Results To Remember

| Model | CVS acc | STG mIoU | TAG@0.3 | DVC F1 | VS LLM | RC LLM |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen2.5-VL-7B SFT | 0.894 | 0.177 | 0.142 | 0.165 | 3.596 | 2.757 |
| Qwen2.5-VL-7B MedGRPO | 0.896 | 0.202 | 0.216 | 0.214 | 4.184 | 3.442 |
| MedGRPO without reward normalization | 0.020 | 0.010 | 0.004 | 0.002 | 3.805 | 3.469 |

## Related

- [Wiki Index](../index.md)
- [Source Catalog](../sources/source-catalog.md)

## Sources

- [MedGRPO paper note](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.md)
- [MedGRPO PDF](../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.pdf)

## Open Questions

- Is MedVidBench fully downloadable, or is access mediated through the project site?
- Does median-centered reward normalization remain stable if the SFT baseline is weak on most dataset-task pairs?
- How much of the medical LLM judge's reliability depends on GPT-4.1 versus the rubric design?
