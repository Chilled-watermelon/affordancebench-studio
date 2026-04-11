#!/usr/bin/env python3
"""
Prompt-only training launcher with an optional TC-Prompt patch.

This keeps the current Trainer/run.log flow intact while forcing the class
encoder to use the same T_plus-aligned text matrix as the historical
prompt-only ablation.
"""
import argparse
import json
import os
import sys
from os.path import join as opj

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
LOCAL_BASE = os.path.join(REPO_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main")
ENV_BASE = os.environ.get("OPENAD_BASE", "")
BASE = ENV_BASE if ENV_BASE else LOCAL_BASE
DEFAULT_PRIORS_JSON = os.environ.get(
    "TC_PRIORS_JSON",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_priors_enhanced_final.json"),
)
DEFAULT_PRIOR_PATH = os.environ.get(
    "TC_PRIOR_PATH",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_prior_features.pt"),
)
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

import clip as clip_pkg
import torch
from gorilla.config import Config

import loss
from utils import (
    IOStream,
    Trainer,
    build_dataset,
    build_loader,
    build_loss,
    build_model,
    build_optimizer,
    set_random_seed,
)


def resolve_model_text_module(model_type):
    if model_type == "openad_pn2":
        import models.openad_pn2 as model_mod
    elif model_type == "openad_dgcnn":
        import models.openad_dgcnn as model_mod
    else:
        raise ValueError(f"TC-Prompt patch is not implemented for model type: {model_type}")
    return model_mod


def parse_args():
    parser = argparse.ArgumentParser(description="Prompt-only launcher with TC text patch")
    parser.add_argument("--config", required=True, help="config py path")
    parser.add_argument(
        "--log_dir",
        "--work_dir",
        dest="work_dir",
        required=True,
        help="输出目录（日志+ckpt）",
    )
    parser.add_argument("--gpu", type=str, default="0", help="逻辑 GPU 编号")
    parser.add_argument("--epoch", type=int, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--weight_counter", type=float, default=None, dest="w_counter")
    parser.add_argument("--weight_infomax", type=float, default=None, dest="w_infomax")
    parser.add_argument("--data_root", type=str, default=None)
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no_tc_loss", action="store_true")
    parser.add_argument(
        "--priors_json",
        type=str,
        default=DEFAULT_PRIORS_JSON,
        help="用于构造 TC-Prompt patch 的 priors json",
    )
    parser.add_argument(
        "--tc_prior_path",
        type=str,
        default=DEFAULT_PRIOR_PATH,
    )
    parser.add_argument(
        "--use_tc_prompt_patch",
        action="store_true",
        help="训练前对 cls_encoder 打与 prompt-only 历史训练一致的 TC patch",
    )
    return parser.parse_args()


def build_tc_prompt_matrix(affordances, priors_path, device):
    with open(priors_path, "r", encoding="utf-8") as handle:
        priors = json.load(handle)

    affordance_to_texts = {aff: [] for aff in affordances}
    for key, value in priors.items():
        if not value.get("is_valid", True):
            continue
        act = key.rsplit("_", 1)[-1]
        if act in affordance_to_texts:
            affordance_to_texts[act].append(value["T_plus"][:220])

    clip_model, _ = clip_pkg.load("ViT-B/32", device=device)
    clip_model.eval()
    for param in clip_model.parameters():
        param.requires_grad_(False)

    repr_texts = [
        affordance_to_texts[aff][0] if affordance_to_texts[aff] else aff
        for aff in affordances
    ]
    with torch.no_grad():
        tokens = clip_pkg.tokenize(repr_texts, truncate=True).to(device)
        aff_feat = clip_model.encode_text(tokens).float()
        aff_feat = aff_feat / aff_feat.norm(dim=-1, keepdim=True)
    return aff_feat.T.contiguous()


def maybe_apply_tc_prompt_patch(cfg, logger, priors_path, device):
    affordances = cfg.training_cfg.train_affordance
    text_feat_fixed = build_tc_prompt_matrix(affordances, priors_path, device)
    model_mod = resolve_model_text_module(cfg.model.type)
    original_forward = model_mod.cls_encoder.forward
    model_mod.cls_encoder.forward = lambda affordance, tf=text_feat_fixed: tf
    logger.cprint(
        "TC-Prompt patch enabled: model=%s priors_json=%s matrix_shape=%s"
        % (cfg.model.type, priors_path, tuple(text_feat_fixed.shape))
    )
    return model_mod, original_forward


def main():
    args = parse_args()
    cfg = Config.fromfile(args.config)

    cfg.work_dir = args.work_dir
    os.makedirs(cfg.work_dir, exist_ok=True)

    cfg.training_cfg.gpu = args.gpu
    if args.epoch is not None:
        cfg.training_cfg.epoch = args.epoch
    if args.batch_size is not None:
        cfg.training_cfg.batch_size = args.batch_size
    if args.w_counter is not None:
        cfg.training_cfg.w_counter = args.w_counter
    if args.w_infomax is not None:
        cfg.training_cfg.w_infomax = args.w_infomax
    if args.data_root is not None:
        cfg.data.data_root = args.data_root
    if getattr(cfg.data, "tc_prior_path", None) in (None, ""):
        cfg.data.tc_prior_path = args.tc_prior_path

    data_root = cfg.data.data_root
    weights_name = (
        "partial_view_weights.npy"
        if cfg.training_cfg.get("partial", False)
        else "full_shape_weights.npy"
    )
    cfg.training_cfg.weights_dir = opj(data_root, weights_name)

    logger = IOStream(opj(cfg.work_dir, "run.log"))
    os.environ["CUDA_VISIBLE_DEVICES"] = cfg.training_cfg.gpu
    logger.cprint("CUDA_VISIBLE_DEVICES=%s" % os.environ.get("CUDA_VISIBLE_DEVICES", ""))
    logger.cprint("work_dir=%s" % cfg.work_dir)
    logger.cprint("data_root=%s weights_dir=%s" % (data_root, cfg.training_cfg.weights_dir))
    logger.cprint(
        "epoch=%s w_counter=%s w_infomax=%s"
        % (
            cfg.training_cfg.epoch,
            cfg.training_cfg.get("w_counter", 0.5),
            cfg.training_cfg.get("w_infomax", 0.05),
        )
    )
    logger.cprint("batch_size=%s" % cfg.training_cfg.batch_size)
    logger.cprint(
        "use_tc_prompt_patch=%s priors_json=%s normal_channel=%s use_geom_side=%s"
        % (
            args.use_tc_prompt_patch,
            args.priors_json,
            cfg.model.get("normal_channel", False),
            cfg.data.get("use_geom_side", False),
        )
    )

    if args.seed is not None:
        cfg.seed = args.seed
    if cfg.get("seed") is not None:
        set_random_seed(cfg.seed)
        logger.cprint("Set seed to %d" % cfg.seed)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    original_forward = None
    patched_model_mod = None
    if args.use_tc_prompt_patch:
        patched_model_mod, original_forward = maybe_apply_tc_prompt_patch(
            cfg, logger, args.priors_json, device
        )

    try:
        model = build_model(cfg).cuda()

        if args.checkpoint:
            logger.cprint("Loading checkpoint: %s" % args.checkpoint)
            ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
            ext = os.path.splitext(args.checkpoint)[1].lower()
            if ext == ".t7":
                model.load_state_dict(
                    ckpt if not isinstance(ckpt, dict) else ckpt.get("model_state_dict", ckpt)
                )
            elif ext == ".pth":
                model.load_state_dict(ckpt["model_state_dict"])
        else:
            logger.cprint("Training from scratch!")

        dataset_dict = build_dataset(cfg)
        loader_dict = build_loader(cfg, dataset_dict)
        train_loss = build_loss(cfg)
        optim_dict = build_optimizer(cfg, model)

        tc_loss = None
        if not args.no_tc_loss:
            tc_loss = loss.TCPriorLoss(
                margin=0.15, tau_danger=0.25, lambda_global=1.5
            ).cuda()

        training = dict(
            model=model,
            dataset_dict=dataset_dict,
            loader_dict=loader_dict,
            loss=train_loss,
            optim_dict=optim_dict,
            logger=logger,
            tc_loss=tc_loss,
        )
        Trainer(cfg, training).run()
    finally:
        if original_forward is not None and patched_model_mod is not None:
            patched_model_mod.cls_encoder.forward = original_forward


if __name__ == "__main__":
    main()
