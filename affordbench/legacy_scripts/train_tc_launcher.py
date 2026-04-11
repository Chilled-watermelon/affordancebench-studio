#!/usr/bin/env python3
"""
TC-Prior 训练入口：支持 --epoch / --weight_counter / --weight_infomax / --log_dir / --data_root / --tc_prior_path
与统帅多线战术命令行对齐；不使用 DDP。
"""
import os
import sys
import argparse
from os.path import join as opj

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
LOCAL_BASE = os.path.join(REPO_ROOT, "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main")
ENV_BASE = os.environ.get("OPENAD_BASE", "")
BASE = ENV_BASE if ENV_BASE else LOCAL_BASE
DEFAULT_PRIOR_PATH = os.environ.get(
    "TC_PRIOR_PATH",
    os.path.join(REPO_ROOT, "assets", "priors", "tc_prior_features.pt"),
)
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

import torch
from gorilla.config import Config

from utils import (
    IOStream,
    set_random_seed,
    build_model,
    build_dataset,
    build_loader,
    build_loss,
    build_optimizer,
    Trainer,
)
import loss


def parse_args():
    p = argparse.ArgumentParser(description="TC-Prior OpenAD train")
    p.add_argument("--config", required=True, help="config py path")
    p.add_argument("--log_dir", "--work_dir", dest="work_dir", required=True, help="输出目录（日志+ckpt）")
    p.add_argument("--gpu", type=str, default="0", help="逻辑 GPU 编号（容器内 0 即物理第 1 张可见卡）")
    p.add_argument("--epoch", type=int, default=None)
    p.add_argument("--batch_size", type=int, default=None)
    p.add_argument("--weight_counter", type=float, default=None, dest="w_counter")
    p.add_argument("--weight_infomax", type=float, default=None, dest="w_infomax")
    p.add_argument("--margin", type=float, default=None)
    p.add_argument("--alpha", type=float, default=None)
    p.add_argument("--delay_epoch_ratio", type=float, default=None)
    p.add_argument("--data_root", type=str, default=None, help="覆盖 cfg.data.data_root")
    p.add_argument("--tc_prior_path", type=str, default=DEFAULT_PRIOR_PATH)
    p.add_argument("--target_affordance", type=str, default=None)
    p.add_argument("--checkpoint", type=str, default=None)
    p.add_argument("--seed", type=int, default=None, help="覆盖 config 的 seed，用于多卡不同初始化")
    p.add_argument("--no_tc_loss", action="store_true", help="完全不挂 TCPriorLoss（纯 NLL）")
    return p.parse_args()


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
    if args.margin is not None:
        cfg.training_cfg.margin = args.margin
    if args.alpha is not None:
        cfg.training_cfg.alpha = args.alpha
    if args.delay_epoch_ratio is not None:
        cfg.training_cfg.delay_epoch_ratio = args.delay_epoch_ratio

    if args.data_root is not None:
        cfg.data.data_root = args.data_root
    # partial_view_cfg 等可能未写 tc_prior_path
    _tp = getattr(cfg.data, "tc_prior_path", None)
    if _tp in (None, ""):
        cfg.data.tc_prior_path = args.tc_prior_path
    if getattr(cfg.data, "target_affordance", None) in (None, ""):
        cfg.data.target_affordance = args.target_affordance or "grasp"

    # weights 与 data_root 一致（避免 /dev/shm 未挂载数据）
    dr = cfg.data.data_root
    if cfg.training_cfg.get("partial", False):
        wname = "partial_view_weights.npy"
    else:
        wname = "full_shape_weights.npy"
    cfg.training_cfg.weights_dir = opj(dr, wname)

    logger = IOStream(opj(cfg.work_dir, "run.log"))
    os.environ["CUDA_VISIBLE_DEVICES"] = cfg.training_cfg.gpu
    logger.cprint("CUDA_VISIBLE_DEVICES=%s" % os.environ.get("CUDA_VISIBLE_DEVICES", ""))
    logger.cprint("work_dir=%s" % cfg.work_dir)
    logger.cprint("data_root=%s weights_dir=%s" % (dr, cfg.training_cfg.weights_dir))
    logger.cprint("epoch=%s w_counter=%s w_infomax=%s" % (
        cfg.training_cfg.epoch,
        cfg.training_cfg.get("w_counter", 0.5),
        cfg.training_cfg.get("w_infomax", 0.05),
    ))
    logger.cprint("batch_size=%s" % cfg.training_cfg.batch_size)
    logger.cprint(
        "margin=%.3f  alpha=%.3f  delay_epoch_ratio=%.2f"
        % (
            float(cfg.training_cfg.get("margin", 0.05)),
            float(cfg.training_cfg.get("alpha", 0.10)),
            float(cfg.training_cfg.get("delay_epoch_ratio", 0.00)),
        )
    )
    logger.cprint(
        "target_affordance=%s tc_prior_path=%s"
        % (cfg.data.get("target_affordance", "grasp"), cfg.data.get("tc_prior_path", ""))
    )

    if args.seed is not None:
        cfg.seed = args.seed
    if cfg.get("seed") is not None:
        set_random_seed(cfg.seed)
        logger.cprint("Set seed to %d" % cfg.seed)

    model = build_model(cfg).cuda()

    if args.checkpoint:
        logger.cprint("Loading checkpoint: %s" % args.checkpoint)
        ext = os.path.splitext(args.checkpoint)[1].lower()

        def _load(p):
            try:
                return torch.load(p, weights_only=False)
            except TypeError:
                return torch.load(p)

        ck = _load(args.checkpoint)
        if ext == ".t7":
            model.load_state_dict(ck if not isinstance(ck, dict) else ck.get("model_state_dict", ck))
        elif ext == ".pth":
            model.load_state_dict(ck["model_state_dict"])
    else:
        logger.cprint("Training from scratch!")

    dataset_dict = build_dataset(cfg)
    loader_dict = build_loader(cfg, dataset_dict)
    train_loss = build_loss(cfg)
    optim_dict = build_optimizer(cfg, model)
    train_set = dataset_dict.get("train_set")
    if train_set is not None and getattr(train_set, "tc_prior_path", None):
        logger.cprint(
            "TC priors loaded: %s (%d keys)"
            % (train_set.tc_prior_path, int(getattr(train_set, "tc_prior_keys", 0)))
        )

    tc_loss = None
    if not args.no_tc_loss:
        margin = float(cfg.training_cfg.get("margin", 0.05))
        alpha = float(cfg.training_cfg.get("alpha", 0.10))
        tc_loss = loss.TCPriorLoss(
            margin=margin,
            alpha=alpha,
            lambda_global=1.5,
        ).cuda()
        logger.cprint("TCPriorLoss 2.0 created: margin=%.3f alpha=%.3f" % (margin, alpha))

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


if __name__ == "__main__":
    main()
