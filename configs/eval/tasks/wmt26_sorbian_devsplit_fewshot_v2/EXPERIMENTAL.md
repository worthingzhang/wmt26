# ⚠️ EXPERIMENTAL / REGRESSED — 非官方 baseline（devsplit_fewshot_v2）

本目录是**内部 few-shot 实验**（v2），**不是 WMT26 官方口径**，且**已证实回归**。

- **已证实 invalid/regressed**：
  - **MT→deu**（dsb-deu / hsb-deu）：指令与抽取正则改成 `<de>`，但示范仍输出 `<deu>`，抽取几乎全 `[invalid]`。
  - **SC、GC**：2-shot 末条为 ERROR，模型 0% 再输出 `CORRECT`，对无错句全判错。
  - 详见 `docs/eval/DEVSPLIT_FEWSHOT_V2_REGRESSION_REPORT.md`。
- 项目主线已于 **2026-06-24** 转为 **official zero-shot**（见 `docs/eval/OFFICIAL_EVAL_ALIGNMENT_PLAN.md`）。
- **暂不修复 v2、不删除任何文件**；配置与跑分**保留供追溯**，但**禁止**作为 baseline 或对外汇报。

官方口径评测使用 `repos/official_eval` 的官方任务（`sorbian_dev` group + QA），与本 overlay **分线**。
