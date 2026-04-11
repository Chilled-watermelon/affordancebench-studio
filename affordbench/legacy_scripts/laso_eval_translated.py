#!/usr/bin/env python3
"""
LASO 测试时指令蒸馏评测（Test-time Prompt Translation Inference）。
用翻译后的极简物理锚点替换原始长句，对比 mIoU。

用法：
  OPENAD_BASE=... CUDA_VISIBLE_DEVICES=3 python laso_eval_translated.py \
    --checkpoint log/tc_prior_run1/best_model.t7 \
    --translated_json /path/to/LASO_dataset/laso_translated_prompts.json \
    --mode both   # 同时评原始和翻译版，输出对比
"""
import os, sys, csv, pickle, json, argparse
import numpy as np
import torch
from tqdm import tqdm
from gorilla.config import Config
import clip as clip_pkg
from typing import Optional


# ── 工具函数 ─────────────────────────────────────────────────────────────────

def load_question_map(csv_path: str, use_all_qs: bool = False) -> dict:
    """(obj_lower, aff_lower) -> question text"""
    m = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            obj = row["Object"].lower().strip()
            aff = row["Affordance"].lower().strip()
            if use_all_qs:
                # 拼接前5个问题，更丰富的语境
                qs = [row.get(f"Question{i}", "").strip() for i in range(5)]
                text = " | ".join(q for q in qs if q)
            else:
                text = (row.get("Question0") or "").strip()
            if text:
                m[(obj, aff)] = text
    return m


def iou_binary(pred_m: np.ndarray, gt_m: np.ndarray) -> Optional[float]:
    inter = (pred_m * gt_m).sum()
    union = np.clip(pred_m + gt_m, 0, 1).sum()
    if union < 1:
        return None
    return float(inter / (union + 1e-8))


def postprocess_minmax(sim: np.ndarray, thresh: float = 0.45) -> np.ndarray:
    """Min-Max 归一化后阈值化"""
    lo, hi = sim.min(), sim.max()
    if hi - lo < 1e-6:
        return np.zeros_like(sim)
    norm = (sim - lo) / (hi - lo)
    return (norm >= thresh).astype(np.float32)


def encode_text(clip_model, text: str, device) -> torch.Tensor:
    tokens = clip_pkg.tokenize([text], truncate=True).to(device)
    with torch.no_grad():
        feat = clip_model.encode_text(tokens)
    return feat / feat.norm(dim=-1, keepdim=True)


def run_eval(model, clip_model, val_annos, objects_val, query_map,
             device, logit_scale, thresh: float = 0.45) -> dict:
    """
    Run inference on all val annotations.
    query_map: (obj, aff) -> query text
    Returns dict with per-affordance IoU and global mIoU.
    """
    per_aff: dict[str, list] = {}
    skipped = 0

    for anno in tqdm(val_annos, desc="Eval", leave=False):
        shape_id = anno["shape_id"]
        cls      = anno["class"].lower().strip()
        aff      = anno["affordance"].lower().strip()
        gt_mask  = np.array(anno["mask"], dtype=np.float32)

        query = query_map.get((cls, aff))
        if not query:
            skipped += 1
            continue

        # 找点云
        pts = None
        for obj in objects_val:
            if obj.get("shape_id") == shape_id or obj.get("id") == shape_id:
                pts = obj.get("coordinate") or obj.get("points")
                break
        if pts is None:
            skipped += 1
            continue

        pts_t = torch.from_numpy(np.array(pts, dtype=np.float32)) \
                     .unsqueeze(0).to(device).permute(0, 2, 1)

        # 文本特征
        txt_feat = encode_text(clip_model, query, device)   # (1, 512)

        # 前向（PN2 返回 3-tuple）
        with torch.no_grad():
            out = model(pts_t, [query])
            if isinstance(out, tuple):
                _, g_i, _ = out          # g_i: (1, N, 512)
            else:
                skipped += 1
                continue

        # 余弦相似度
        g_norm = g_i / (g_i.norm(dim=-1, keepdim=True) + 1e-8)  # (1, N, 512)
        sim    = (g_norm @ txt_feat.T).squeeze(-1).squeeze(0).cpu().numpy()  # (N,)

        pred = postprocess_minmax(sim, thresh)
        iou  = iou_binary(pred, gt_mask)
        if iou is None:
            skipped += 1
            continue

        per_aff.setdefault(aff, []).append(iou)

    global_ious = [v for vals in per_aff.values() for v in vals]
    miou = float(np.mean(global_ious)) if global_ious else 0.0

    per_aff_mean = {a: float(np.mean(v)) for a, v in per_aff.items()}
    return {
        "global_miou": miou,
        "n_samples": len(global_ious),
        "n_skipped": skipped,
        "per_affordance": per_aff_mean,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--openad_base",
        default=os.environ.get(
            "OPENAD_BASE",
            "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main",
        ),
    )
    ap.add_argument("--config", default="config/openad_pn2/full_shape_cfg.py")
    ap.add_argument("--checkpoint",
                    default="log/tc_prior_run1/best_model.t7")
    ap.add_argument("--laso_root",
                    default=os.environ.get("LASO_ROOT", "LASO_dataset"))
    ap.add_argument("--translated_json",
                    default=None)
    ap.add_argument("--mode",
                    choices=["original", "translated", "both"],
                    default="both",
                    help="评原始、翻译版或两者都评（对比）")
    ap.add_argument("--thresh", type=float, default=0.45)
    ap.add_argument("--gpu",    default="0")
    args = ap.parse_args()

    base = os.path.abspath(args.openad_base)
    if base not in sys.path:
        sys.path.insert(0, base)
    os.chdir(base)

    from utils import build_model

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    device = torch.device("cuda:0")

    config_path = (
        args.config if os.path.isabs(args.config) else os.path.join(base, args.config)
    )
    checkpoint_path = (
        args.checkpoint
        if os.path.isabs(args.checkpoint)
        else os.path.join(base, args.checkpoint)
    )
    translated_json = args.translated_json or os.path.join(
        args.laso_root, "laso_translated_prompts.json"
    )

    # ── 加载模型 ─────────────────────────────────────────────────────────────
    cfg = Config.fromfile(config_path)
    cfg.training_cfg.gpu = args.gpu

    model = build_model(cfg).to(device)
    ck = torch.load(checkpoint_path, map_location=device, weights_only=False)
    sd = ck.get("model_state_dict", ck) if isinstance(ck, dict) else ck
    model.load_state_dict(sd)
    model.eval()
    print(f"Model loaded from {args.checkpoint}")

    # ── 加载 CLIP ─────────────────────────────────────────────────────────────
    clip_model, _ = clip_pkg.load("ViT-B/32", device=device)
    clip_model.eval()
    logit_scale = clip_model.logit_scale.exp().item()

    # ── 加载 LASO 数据 ────────────────────────────────────────────────────────
    laso = args.laso_root
    with open(os.path.join(laso, "anno_val.pkl"),    "rb") as f:
        val_annos = pickle.load(f)
    with open(os.path.join(laso, "objects_val.pkl"), "rb") as f:
        objects_val = pickle.load(f)

    csv_path = os.path.join(laso, "Affordance-Question.csv")
    print(f"Val annotations: {len(val_annos)}")

    results = {}

    # ── 评原始长句版 ──────────────────────────────────────────────────────────
    if args.mode in ("original", "both"):
        print("\n[ORIGINAL long-sentence queries]")
        orig_map = load_question_map(csv_path)
        res_orig = run_eval(model, clip_model, val_annos, objects_val,
                            orig_map, device, logit_scale, args.thresh)
        results["original"] = res_orig
        print(f"  Global mIoU = {res_orig['global_miou']:.4f}  "
              f"({res_orig['n_samples']} samples, {res_orig['n_skipped']} skipped)")

    # ── 评翻译版 ──────────────────────────────────────────────────────────────
    if args.mode in ("translated", "both"):
        if not os.path.exists(translated_json):
            print(f"\nERROR: translated_json not found: {translated_json}")
            print("Please run laso_translate_prompts.py first.")
            return

        print(f"\n[TRANSLATED physical-anchor queries from {translated_json}]")
        with open(translated_json, encoding="utf-8") as f:
            trans_raw = json.load(f)
        # trans_raw key format: "obj_aff"  →  translate back to (obj, aff) tuple
        trans_map = {}
        for key, val in trans_raw.items():
            parts = key.split("_", 1)
            if len(parts) == 2:
                trans_map[(parts[0], parts[1])] = val

        res_trans = run_eval(model, clip_model, val_annos, objects_val,
                             trans_map, device, logit_scale, args.thresh)
        results["translated"] = res_trans
        print(f"  Global mIoU = {res_trans['global_miou']:.4f}  "
              f"({res_trans['n_samples']} samples, {res_trans['n_skipped']} skipped)")

    # ── 对比报告 ──────────────────────────────────────────────────────────────
    if args.mode == "both" and "original" in results and "translated" in results:
        orig  = results["original"]["global_miou"]
        trans = results["translated"]["global_miou"]
        delta = trans - orig
        print(f"\n{'='*55}")
        print(f"  LASO 测试时指令蒸馏对比结果")
        print(f"{'='*55}")
        print(f"  原始长句版  mIoU = {orig:.4f}  ({orig*100:.2f}%)")
        print(f"  翻译锚点版  mIoU = {trans:.4f}  ({trans*100:.2f}%)")
        print(f"  Δ mIoU     = {delta:+.4f}  ({delta*100:+.2f}%)")
        if delta > 0:
            rel = delta / (orig + 1e-8) * 100
            print(f"  相对提升   = +{rel:.1f}%  ← 云-端协同蒸馏生效！")
        print(f"{'='*55}")

        # 保存结果 JSON
        out_json = os.path.join(base, "results", "laso_translation_comparison.json")
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        with open(out_json, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to: {out_json}")


if __name__ == "__main__":
    main()
