#!/usr/bin/env python3
"""
LASO Test-time Prompt Translation
将 LASO Affordance-Question.csv 中所有长句翻译为极简物理常识锚点格式，
供 TC-Prior CLIP 编码使用。

用法（本地 CPU，无需 GPU）：
  OPENAI_API_KEY=... python laso_translate_prompts.py \
    --csv LASO_dataset/Affordance-Question.csv \
    --out LASO_dataset/laso_translated_prompts.json
"""
import os
import csv, json, time, argparse
from pathlib import Path
from tqdm import tqdm
try:
    from openai import OpenAI
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

# ── API 配置 ──────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api2.qiandao.mom/v1")
MODEL = os.environ.get("OPENAI_MODEL", "gemini-3.1-pro-preview-h")

# ── System Prompt（一字不改）────────────────────────────────────────────────
SYSTEM_PROMPT = """
你是一个具身智能（Embodied AI）指令翻译器。
你的任务是将人类冗长、复杂的自然语言交互指令，提取为极简的、结构化的【物理常识锚点】。
你需要识别出用户想要安全交互的目标部件（Target），以及需要避开的危险部件（Danger）及其后果（Consequence）。

输出必须严格遵循以下格式（不要输出任何其他多余的解释）：
[Target] <安全交互区域描述> [Danger] <高危区域描述> [Consequence] <物理危险后果>

示例输入: "If I want to safely hand this knife to someone, where should I hold it?"
示例输出: [Target] safe handle [Danger] sharp blade [Consequence] cut hazard
"""

client = OpenAI(api_key=API_KEY, base_url=API_BASE) if API_KEY else None


def translate_prompt(original: str, retries: int = 3) -> str:
    if client is None:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Export OPENAI_API_KEY before running this script."
        )
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": original},
                ],
                temperature=0.1,
                stream=False,
                max_tokens=80,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    # fallback: 直接用精简的 affordance 名称
    return original[:80]


def main():
    ap = argparse.ArgumentParser()
    laso_root = os.environ.get("LASO_ROOT", "LASO_dataset")
    ap.add_argument("--csv",    default=os.path.join(laso_root, "Affordance-Question.csv"))
    ap.add_argument("--out",    default=os.path.join(laso_root, "laso_translated_prompts.json"))
    ap.add_argument("--resume", action="store_true", help="续跑，跳过已翻译的")
    args = ap.parse_args()

    # 读已有结果（续跑支持）
    out_path = Path(args.out)
    result: dict = {}
    if args.resume and out_path.exists():
        with open(out_path) as f:
            result = json.load(f)
        print(f"Resumed: {len(result)} entries already done.")

    # 读 CSV
    rows = []
    with open(args.csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    print(f"Total CSV rows: {len(rows)}")
    total_cost = 0

    for row in tqdm(rows, desc="Translating"):
        obj = row["Object"].lower().strip()
        aff = row["Affordance"].lower().strip()
        key = f"{obj}_{aff}"

        if key in result:
            continue

        # 用 Question0（最具代表性的长句）
        q0 = (row.get("Question0") or "").strip()
        # 也可补充 ExplanatoryQuestion1 获得更丰富的上下文
        expl = (row.get("ExplanatoryQuestion1") or "").strip()
        full_q = q0 if not expl else f"{q0} ({expl})"

        if not q0:
            result[key] = f"[Target] {aff} region [Danger] unsafe region [Consequence] injury"
            continue

        translated = translate_prompt(full_q)
        result[key] = translated
        total_cost += 1

        # 每 10 条保存一次（断点续跑）
        if total_cost % 10 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n  Saved {len(result)} entries at cost {total_cost} calls")

    # 最终保存
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Total entries: {len(result)}")
    print(f"API calls made: {total_cost}")
    print(f"Saved to: {out_path}")

    # 打印10条样本展示效果
    print("\n=== Sample translations ===")
    for i, (k, v) in enumerate(list(result.items())[:10]):
        print(f"[{k}] => {v}")


if __name__ == "__main__":
    main()
