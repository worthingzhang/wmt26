# ⚠️ EXPERIMENTAL / REGRESSED — 非官方 baseline（devsplit_fewshot_v2 数据）

本目录是 `devsplit_fewshot_v2` 实验 profile 的配套 devsplit 数据（shots / 抽样清单），**内部实验用**，**非 WMT26 官方口径**，且对应跑分已证实回归。

- v2 的 MT→deu、SC、GC 已证实 **invalid/regressed**（见 `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md`）。
- 主线已转 **official zero-shot**（见 `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md`）。
- **暂不修复、不删除**；保留供追溯，不得用作官方 baseline。

配套任务配置见 `configs/eval/tasks/wmt26_sorbian_devsplit_fewshot_v2/EXPERIMENTAL.md`。
