#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import torch

try:
    import clip as clip_pkg
except ImportError:
    clip_pkg = None

try:
    from transformers import CLIPModel, CLIPTokenizer
except ImportError:
    CLIPModel = None
    CLIPTokenizer = None


def encode_texts(model, tokenizer, device, texts):
    if clip_pkg is not None and tokenizer is None:
        tokens = clip_pkg.tokenize(texts, truncate=True).to(device)
        with torch.no_grad():
            feats = model.encode_text(tokens).float()
            feats = feats / feats.norm(dim=-1, keepdim=True).clamp_min(1e-12)
        return feats.cpu()

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt",
    ).to(device)
    with torch.no_grad():
        feats = model.get_text_features(**inputs).float()
        feats = feats / feats.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return feats.cpu()


def main():
    default_assets_root = Path(__file__).resolve().parents[1] / "assets" / "priors"
    parser = argparse.ArgumentParser(description="Extract CLIP features for TC-Prior texts")
    parser.add_argument(
        "--input_json",
        default=os.environ.get(
            "TC_PRIORS_JSON",
            str(default_assets_root / "tc_priors_enhanced_final.json"),
        ),
    )
    parser.add_argument(
        "--output_pt",
        default=os.environ.get(
            "TC_PRIOR_FEATURES_PT",
            str(default_assets_root / "tc_prior_features.pt"),
        ),
    )
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    input_path = Path(args.input_json)
    output_path = Path(args.output_pt)
    payload = json.loads(input_path.read_text(encoding="utf-8"))

    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")
    tokenizer = None
    if clip_pkg is not None:
        model, _ = clip_pkg.load("ViT-B/32", device=device)
        model.eval()
        for param in model.parameters():
            param.requires_grad_(False)
    else:
        if CLIPModel is None or CLIPTokenizer is None:
            raise RuntimeError("Neither `clip` nor `transformers` CLIP is available.")
        tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        model.eval()
        for param in model.parameters():
            param.requires_grad_(False)

    encoded = {}
    valid = 0
    skipped = 0
    for key, value in payload.items():
        if not value.get("is_valid", True):
            skipped += 1
            continue
        text_plus = (value.get("T_plus") or "").strip()
        text_minus = (value.get("T_minus") or "").strip()
        if not text_plus or not text_minus:
            skipped += 1
            continue
        feats = encode_texts(model, tokenizer, device, [text_plus, text_minus])
        encoded[key] = {
            "T_plus": feats[0],
            "T_minus": feats[1],
            "text_T_plus": text_plus,
            "text_T_minus": text_minus,
        }
        valid += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(encoded, output_path)
    print(f"saved: {output_path}")
    print(f"valid_pairs: {valid}")
    print(f"skipped_pairs: {skipped}")


if __name__ == "__main__":
    main()
