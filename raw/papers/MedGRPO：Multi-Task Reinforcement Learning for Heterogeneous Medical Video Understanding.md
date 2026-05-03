# Paper Note: MedGRPO: Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding

Source type: paper
Status: Distilled
Date added: 2026-05-03

## Bibliography

- Title: MedGRPO: Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding
- Authors: Yuhao Su, Anwesa Choudhuri, Zhongpai Gao, Benjamin Planche, Van Nguyen Nguyen, Meng Zheng, Yuhan Shen, Arun Innanje, Terrence Chen, Ehsan Elhamifar, Ziyan Wu
- Year: 2026
- Venue: arXiv
- arXiv: 2512.06581v4
- URL: https://uii-america.github.io/MedGRPO/
- Local file: `../../raw/papers/MedGRPO：Multi-Task Reinforcement Learning for Heterogeneous Medical Video Understanding.pdf`

## Why It Matters

This paper is useful for understanding how reinforcement learning for vision-language models can fail on heterogeneous medical video tasks when reward scales are not balanced. It also provides a concrete recipe for building a medical video instruction benchmark from existing expert annotations.

## Reading Notes

- The paper introduces MedVidBench, a 531,850-sample medical video instruction benchmark built from 8 medical video sources and 8 task types.
- The benchmark spans laparoscopic surgery, open surgery, robotic surgery, and nursing procedures.
- Tasks are organized across three granularities:
  - Video-level: video summarization, critical view of safety, next action prediction, skill assessment.
  - Segment-level: temporal action grounding, dense video captioning, region captioning.
  - Frame-level: spatiotemporal grounding.
- The authors transform existing expert annotations into instruction-following QA pairs rather than annotating from scratch.
- Their data pipeline uses source-specific prompting:
  - Bounding boxes and labels are overlaid on frames for densely annotated surgical datasets.
  - Whisper-X transcripts and metadata are used for web-sourced medical videos.
  - GPT-4.1 and Gemini-2.5-Flash generate captions independently for validation.
- Naive GRPO on the heterogeneous dataset collapses because easy datasets produce consistently higher raw rewards than harder datasets.
- MedGRPO fixes this with dataset-task-specific logistic reward normalization centered on each dataset-task median.
- The normalization maps median performance for every dataset-task pair to reward 0.5, reducing bias toward easy datasets.
- For captioning tasks, semantic similarity is insufficient because clinically important differences can be hidden by high embedding similarity.
- The paper adds a medical LLM judge that evaluates caption quality on five dimensions:
  - Medical terminology precision.
  - Instrument and anatomy identification.
  - Specificity versus vagueness.
  - Clinical procedure context.
  - Action and state accuracy.
- The final caption reward averages normalized semantic similarity and the medical LLM judge score.
- SFT on MedVidBench greatly improves Qwen2.5-VL-7B over off-the-shelf GPT-4.1, Gemini-2.5-Flash, and Qwen2.5-VL-7B baselines.
- MedGRPO further improves the SFT baseline on most evaluated tasks, especially grounding and captioning.
- Removing reward normalization causes catastrophic collapse in the ablation, dropping CVS from 0.894 SFT to 0.020 and STG from 0.177 to 0.010.
- Training with caption tasks also improves grounding performance, suggesting useful multi-task transfer between descriptive and localization objectives.
- The medical LLM judge is validated against board-certified clinician ratings, with reported Pearson correlation 0.977 and Cohen's Kappa 0.817.

## Claims To Distill

- In heterogeneous multi-dataset RL, raw task metrics can create unfair reward scales that bias optimization toward easy datasets.
- Median-centered reward normalization can make dataset-task pairs comparable without erasing within-dataset ranking information.
- Domain-specific evaluation is necessary for medical captioning because general semantic similarity misses instrument, anatomy, action, and spatial precision.
- Multi-task medical video training benefits from connecting captioning and grounding tasks rather than optimizing them in isolation.
- Strong general VLMs still need domain adaptation for medical video understanding, especially for grounding tasks.

## Methods And Evidence

- Dataset: MedVidBench, 531,850 video-instruction pairs across 626 videos, 8 medical sources, and 8 task types.
- Model/system: Qwen2.5-VL-7B SFT baseline, followed by MedGRPO reinforcement learning; also evaluated on Qwen3-VL-4B and Qwen3.5-4B variants.
- Reward design:
  - Dataset-task logistic normalization using SFT baseline percentiles.
  - Median performance maps to normalized reward 0.5.
  - IQR scaling reduces outlier sensitivity.
  - Caption tasks combine semantic similarity and medical LLM judge score.
- Evaluation:
  - Accuracy for CVS, NAP, and skill assessment.
  - mIoU for spatiotemporal grounding and temporal action grounding.
  - LLM judge scores and F1 for captioning tasks.
- Main result:
  - Qwen2.5-VL-7B SFT reaches 0.894 CVS, 0.177 STG, 0.142 TAG@0.3, 3.596 VS LLM, and 2.757 RC LLM.
  - Qwen2.5-VL-7B MedGRPO improves to 0.896 CVS, 0.202 STG, 0.216 TAG@0.3, 4.184 VS LLM, and 3.442 RC LLM.
  - NAP decreases from 0.442 to 0.405 because it was not one of the optimized reward tasks.

## Related Work

- GRPO and DAPO-style reinforcement learning for language or vision-language models.
- Medical video datasets such as CholecT50, CholecTrack20, Cholec80-CVS, CoPESD, AVOS, EgoSurgery, JIGSAWS, and NurViD.
- LLM-as-a-judge evaluation for domain-specific caption quality.
- Medical video-language models and instruction tuning.

## Follow-ups

- Check whether MedVidBench is publicly downloadable or only described through the project website.
- Inspect the released code to see how the reward normalization statistics are computed and stored.
- Compare this median-centered normalization with z-score, percentile rank, and per-task advantage normalization.
- Evaluate whether the medical LLM judge prompt can be reused for non-video medical image captioning tasks.
