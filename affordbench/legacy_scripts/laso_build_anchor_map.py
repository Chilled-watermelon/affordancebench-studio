#!/usr/bin/env python3
"""
LASO 测试时指令蒸馏 —— 规则模板版（无需 LLM API，秒级完成）

策略：把 LASO 的长句问题替换为 CLIP 最熟悉的极简物理描述。
对比：
  原始: "If I want to safely hand this knife to someone, where should I hold it?"  (CLIP 困惑)
  ours: "safe grasping area of knife handle"                                        (CLIP 精准)

用法：
  python laso_build_anchor_map.py --out laso_anchor_map.json
"""
import json, csv, argparse
import os

# ── 可供性 → CLIP 友好短语（物理常识锚点） ────────────────────────────────
AFF_PHRASE = {
    # 抓握类
    "grasp":      "graspable handle area for safe gripping",
    "grab":       "graspable handle area for safe gripping",

    # 坐躺类
    "sit":        "stable seat surface for sitting",
    "lay":        "flat soft surface for lying down",
    "rest":       "supportive resting surface",

    # 包含 / 承重
    "contain":    "open container cavity for holding objects",
    "support":    "flat stable surface for placing objects",
    "bear":       "weight-bearing load surface",

    # 提拉 / 移动
    "lift":       "balanced lifting point for raising object",
    "move":       "secure grip region for moving or repositioning",
    "push":       "flat pushable surface area",
    "pull":       "graspable pull point or handle",

    # 工具操作
    "cut":        "sharp blade cutting edge",
    "stab":       "pointed tip for piercing",
    "press":      "pressable button or surface",
    "open":       "openable latch or handle mechanism",
    "pour":       "spout or opening for pouring liquid",

    # 穿戴 / 使用
    "wear":       "wearable strap or band contact zone",
    "wrap":       "flexible wrap-around gripping region",
    "listen":     "speaker or audio output surface",

    # 展示 / 其他
    "display":    "flat display viewing surface",
    "displace":   "movable displacement region",
    "displaY":    "flat display viewing surface",

    # 桌椅家具
    "sittable":   "stable seated area",
    "layable":    "horizontal resting surface",
    "openable":   "hinged opening mechanism",
    "pourable":   "liquid dispensing spout region",
    "pushable":   "flat pushable surface",
    "wrap_grasp": "wrap-around gripping region",
}

# ── 物体 → 细化描述（可选，增强语义） ────────────────────────────────────
OBJ_HINT = {
    "knife":    "of knife blade and handle",
    "scissors": "of scissors handles and blades",
    "mug":      "of mug handle and cup body",
    "cup":      "of cup handle and rim",
    "bag":      "of bag strap and body",
    "chair":    "of chair seat and back",
    "bed":      "of bed mattress surface",
    "table":    "of table flat top surface",
    "door":     "of door handle and panel",
    "bowl":     "of bowl rim and interior",
    "bottle":   "of bottle neck and body",
    "laptop":   "of laptop keyboard and screen",
    "hat":      "of hat brim and crown",
    "vase":     "of vase neck and body",
}


def build_anchor(obj: str, aff: str) -> str:
    """构建极简物理锚点描述"""
    aff_l = aff.lower().strip()
    obj_l = obj.lower().strip()

    phrase = AFF_PHRASE.get(aff_l, f"{aff_l} interaction region")
    hint   = OBJ_HINT.get(obj_l, f"of {obj_l}")

    return f"{phrase} {hint}"


def main():
    ap = argparse.ArgumentParser()
    laso_root = os.environ.get("LASO_ROOT", "LASO_dataset")
    ap.add_argument("--csv", default=os.path.join(laso_root, "Affordance-Question.csv"))
    ap.add_argument("--out", default=os.path.join(laso_root, "laso_anchor_map.json"))
    ap.add_argument("--show_samples", type=int, default=20)
    args = ap.parse_args()

    result = {}
    with open(args.csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            obj = row["Object"].strip()
            aff = row["Affordance"].strip()
            key = f"{obj.lower()}_{aff.lower()}"
            anchor = build_anchor(obj, aff)
            orig   = (row.get("Question0") or "").strip()
            result[key] = {
                "anchor":   anchor,
                "original": orig,
                "object":   obj,
                "affordance": aff,
            }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Built {len(result)} anchors → {args.out}")
    print(f"\n=== Sample anchors (first {args.show_samples}) ===")
    for i, (k, v) in enumerate(list(result.items())[:args.show_samples]):
        print(f"  [{k}]")
        print(f"    ORIG:   {v['original'][:70]}...")
        print(f"    ANCHOR: {v['anchor']}")
        print()


if __name__ == "__main__":
    main()
