from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    name: str
    script: str
    category: str
    description: str
    runner: str = "python"
    notes: str = ""
    example: str = ""


COMMANDS = {
    "env-check": CommandSpec(
        name="env-check",
        script="affordbench_env_check.py",
        category="core",
        description="检查 OPENAD_BASE / LASO_ROOT 与关键文件是否到位",
        notes="最适合作为所有公开 workflow 的第一个命令。",
        example="affordbench env-check -- --mode openad",
    ),
    "train-tc": CommandSpec(
        name="train-tc",
        script="train_tc_launcher.py",
        category="train",
        description="TC-Prior 训练入口",
        example="affordbench train-tc -- --config config/openad_pn2/full_shape_cfg.py --log_dir log/exp1",
    ),
    "train-prompt": CommandSpec(
        name="train-prompt",
        script="train_promptonly_tcpatch_launcher.py",
        category="train",
        description="Prompt-only 训练入口",
        example="affordbench train-prompt -- --config config/openad_pn2/full_shape_cfg.py --log_dir log/prompt_only",
    ),
    "eval-risk": CommandSpec(
        name="eval-risk",
        script="eval_risk_subset_with_tc_patch.py",
        category="eval",
        description="通用 risk subset 评测入口",
        example="affordbench eval-risk -- --config config/openad_pn2/full_shape_cfg.py --checkpoint log/model/best_model.t7",
    ),
    "eval-ablation": CommandSpec(
        name="eval-ablation",
        script="eval_ablation_bc_risk_subset.py",
        category="eval",
        description="Ablation B/C 风险子集评测",
        example="affordbench eval-ablation -- --tag B --ckpt log/ablation_B_no_repulsion/best_model.t7",
    ),
    "eval-boundary": CommandSpec(
        name="eval-boundary",
        script="eval_boundary_metrics.py",
        category="eval",
        description="边界敏感指标评测与对象级聚合",
        example="affordbench eval-boundary -- --config config/openad_pn2/full_shape_cfg.py --checkpoint log/model/best_model.t7",
    ),
    "eval-interaction-proxy": CommandSpec(
        name="eval-interaction-proxy",
        script="eval_interaction_proxy.py",
        category="eval",
        description="交互代理指标评测",
        example="affordbench eval-interaction-proxy -- --config config/openad_pn2/full_shape_cfg.py --checkpoint log/model/best_model.t7",
    ),
    "rerun-ablation": CommandSpec(
        name="rerun-ablation",
        script="rerun_ablation_eval.py",
        category="eval",
        description="重跑早期 ablation 对比评测",
        notes="更偏历史审计修复，但作为 reproducibility 工具仍有价值。",
    ),
    "laso-qaq": CommandSpec(
        name="laso-qaq",
        script="gpu3_laso_q_as_q.py",
        category="laso",
        description="LASO Question-as-Query 零样本入口",
        example="affordbench laso-qaq -- --checkpoint log/tc_prior_run1/best_model.t7",
    ),
    "laso-zeroshot": CommandSpec(
        name="laso-zeroshot",
        script="gpu3_laso_zeroshot.py",
        category="laso",
        description="LASO affordance 映射零样本入口",
        example="affordbench laso-zeroshot -- --checkpoint log/tc_prior_run1/best_model.t7",
    ),
    "laso-translate": CommandSpec(
        name="laso-translate",
        script="laso_translate_prompts.py",
        category="laso",
        description="把 LASO 长句翻成更可控的 query 文本",
        notes="公开版必须通过环境变量注入 API key，不能硬编码。",
    ),
    "laso-anchor-map": CommandSpec(
        name="laso-anchor-map",
        script="laso_build_anchor_map.py",
        category="laso",
        description="基于规则模板生成 LASO anchor map",
        example="affordbench laso-anchor-map -- --out \"$LASO_ROOT/laso_anchor_map.json\"",
    ),
    "laso-eval-translated": CommandSpec(
        name="laso-eval-translated",
        script="laso_eval_translated.py",
        category="laso",
        description="评测原始 query 与 translated query 的对比",
    ),
    "extract-priors": CommandSpec(
        name="extract-priors",
        script="extract_clip_priors.py",
        category="priors",
        description="为先验文本抽取 CLIP 特征",
    ),
    "preprocess-priors": CommandSpec(
        name="preprocess-priors",
        script="preprocess_priors.py",
        category="priors",
        description="标准化先验文本格式",
    ),
    "macc-compare": CommandSpec(
        name="macc-compare",
        script="gpu3_macc_compare.py",
        category="eval",
        description="公平 mAcc 对比",
    ),
    "render-heatmap": CommandSpec(
        name="render-heatmap",
        script="render_heatmap.py",
        category="viz",
        description="渲染热力图 figure",
        example="affordbench render-heatmap -- --root \"$OPENAD_BASE\" --ckpt_ours log/tc_prior_run1/best_model.t7",
    ),
    "visualize-tsne": CommandSpec(
        name="visualize-tsne",
        script="visualize_tsne.py",
        category="viz",
        description="渲染 t-SNE feature space figure",
    ),
    "render-failure-cases": CommandSpec(
        name="render-failure-cases",
        script="render_failure_cases.py",
        category="viz",
        description="渲染附录失败案例",
    ),
    "plot-sensitivity": CommandSpec(
        name="plot-sensitivity",
        script="plot_hyperparameter_sensitivity.py",
        category="viz",
        description="绘制训练曲线与超参数敏感性图",
    ),
    "profile-efficiency": CommandSpec(
        name="profile-efficiency",
        script="profile_efficiency.py",
        category="profile",
        description="模型效率 profiling（Params/FLOPs/Latency/FPS）",
        notes="适合 Open Source track paper 中证明 technical depth 与 buildability。",
        example="affordbench profile-efficiency -- --config config/openad_pn2/estimation_cfg.py --device cpu",
    ),
    "profile-stage-breakdown": CommandSpec(
        name="profile-stage-breakdown",
        script="profile_stage_breakdown.py",
        category="profile",
        description="分阶段端到端 proxy 开销 profiling",
    ),
    "generate-backup-manifest": CommandSpec(
        name="generate-backup-manifest",
        script="generate_private_backup_manifest.py",
        category="ops",
        description="生成私有备份 manifest",
    ),
    "gdrive-download": CommandSpec(
        name="gdrive-download",
        script="gdrive_download.py",
        category="ops",
        description="按 file id 下载 Google Drive 文件",
    ),
    "gdrive-resume": CommandSpec(
        name="gdrive-resume",
        script="drive_download_resume.py",
        category="ops",
        description="带续传的 Google Drive 下载",
    ),
    "run-figures-gpu3": CommandSpec(
        name="run-figures-gpu3",
        script="run_figures_gpu3.sh",
        category="ops",
        description="串行运行 Figure 3/5 生成脚本",
        runner="shell",
        notes="更适合 Linux/GPU 机器；公开版可作为 batch workflow 示例。",
    ),
    "run-dgcnn-seeds": CommandSpec(
        name="run-dgcnn-seeds",
        script="run_dgcnn_corl_three_seeds.sh",
        category="ops",
        description="启动 DGCNN 三 seed 训练打包流程",
        runner="shell",
    ),
    "eval-dgcnn-package": CommandSpec(
        name="eval-dgcnn-package",
        script="eval_dgcnn_corl_package.sh",
        category="ops",
        description="聚合 DGCNN 三 seed 评测包",
        runner="shell",
    ),
    "package-backup-assets": CommandSpec(
        name="package-backup-assets",
        script="package_private_backup_assets.sh",
        category="ops",
        description="打包大文件冷备份分卷",
        runner="shell",
    ),
}
