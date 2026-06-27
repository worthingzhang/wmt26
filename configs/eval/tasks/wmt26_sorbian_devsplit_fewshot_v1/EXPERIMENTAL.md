# ⚠️ EXPERIMENTAL — 非官方 baseline（devsplit_fewshot_v1）

本目录是**内部 few-shot 实验**（v1），**不是 WMT26 官方口径**。

- 项目主线已于 **2026-06-24** 转为 **official zero-shot**（见 `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md`）。
- v1 比 v2 稳定，但其 SC/GC 的较高分本质是“恰好被 CORRECT 示范 priming”，**非真实纠错能力**（见 `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md` §5.4），**不得**用作官方 baseline 或对外汇报。
- 配置与既往跑分**保留供追溯**，暂不删除。

官方口径评测使用 `repos/official_eval` 的官方任务（`sorbian_dev` group + QA），与本 overlay **分线**。
