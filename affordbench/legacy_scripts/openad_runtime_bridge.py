#!/usr/bin/env python3
"""Compatibility helpers for running OpenAD PointNet++ scripts safely."""

import importlib
import importlib.util
import os
import sys
import types
from pathlib import Path
from typing import Optional, Union

import torch

BASE = os.environ.get(
    "OPENAD_BASE",
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main",
    ),
)
BASE = os.path.abspath(BASE)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

OPENAD_MODELS_DIR = Path(BASE) / "models"
OPENAD_MODEL_PACKAGE = "affordbench_runtime_openad_models"


def maybe_add_clip_root(base: Optional[Union[str, os.PathLike]] = None) -> None:
    candidates = []
    env_root = os.environ.get("OPENAI_CLIP_ROOT", "")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    base_path = Path(base or BASE)
    candidates.extend(
        [
            base_path / "openai_CLIP",
            base_path.parent / "openai_CLIP",
            base_path.parent.parent / "openai_CLIP",
        ]
    )

    seen = set()
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
        except FileNotFoundError:
            candidate = candidate.expanduser()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "clip" / "__init__.py").is_file():
            sys.path.insert(0, str(candidate))
            os.environ.setdefault("OPENAI_CLIP_ROOT", str(candidate))
            return


maybe_add_clip_root()


def force_cpu_clip_load():
    try:
        import clip as clip_pkg
    except ImportError:
        return None, None

    original_load = clip_pkg.load

    def patched_load(name, device="cpu", *args, **kwargs):
        return original_load(name, device="cpu", *args, **kwargs)

    clip_pkg.load = patched_load
    return clip_pkg, original_load


def prepare_device(device_name: str):
    requested = device_name.lower()
    actual = requested
    restore_cuda_is_available = None
    restore_clip_load = None

    if requested == "cuda" and not torch.cuda.is_available():
        actual = "cpu"
    if actual == "cpu":
        restore_cuda_is_available = torch.cuda.is_available
        torch.cuda.is_available = lambda: False
        _, restore_clip_load = force_cpu_clip_load()

    return torch.device("cuda:0" if actual == "cuda" else "cpu"), actual, restore_cuda_is_available, restore_clip_load


def restore_device_runtime(restore_cuda_is_available, restore_clip_load) -> None:
    if restore_clip_load is not None:
        import clip as clip_pkg

        clip_pkg.load = restore_clip_load
    if restore_cuda_is_available is not None:
        torch.cuda.is_available = restore_cuda_is_available


class PN2_Scheduler(object):
    def __init__(self, init_lr, step, decay_rate, min_lr):
        self.init_lr = init_lr
        self.step = step
        self.decay_rate = decay_rate
        self.min_lr = min_lr

    def __call__(self, epoch):
        factor = self.decay_rate ** (epoch // self.step)
        if self.init_lr * factor < self.min_lr:
            factor = self.min_lr / self.init_lr
        return factor


class PN2_BNMomentum(object):
    def __init__(self, origin_m, m_decay, step):
        self.origin_m = origin_m
        self.m_decay = m_decay
        self.step = step

    def __call__(self, module, epoch):
        momentum = self.origin_m * (self.m_decay ** (epoch // self.step))
        if momentum < 0.01:
            momentum = 0.01
        if isinstance(module, (torch.nn.BatchNorm2d, torch.nn.BatchNorm1d)):
            module.momentum = momentum


def install_config_utils_shim():
    original = sys.modules.get("utils")
    shim = types.ModuleType("utils")
    shim.PN2_BNMomentum = PN2_BNMomentum
    shim.PN2_Scheduler = PN2_Scheduler
    sys.modules["utils"] = shim
    return original


def restore_config_utils_shim(original_utils) -> None:
    if original_utils is None:
        sys.modules.pop("utils", None)
    else:
        sys.modules["utils"] = original_utils


def load_openad_config(config_path: str):
    original_utils = install_config_utils_shim()
    try:
        from gorilla.config import Config

        return Config.fromfile(config_path)
    finally:
        restore_config_utils_shim(original_utils)


def ensure_openad_model_package() -> None:
    if OPENAD_MODEL_PACKAGE in sys.modules:
        return
    package = types.ModuleType(OPENAD_MODEL_PACKAGE)
    package.__path__ = [str(OPENAD_MODELS_DIR)]
    sys.modules[OPENAD_MODEL_PACKAGE] = package


def load_openad_submodule(name: str):
    ensure_openad_model_package()
    module_name = f"{OPENAD_MODEL_PACKAGE}.{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = OPENAD_MODELS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create import spec for {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def patch_legacy_class_encoder(model_mod, device: torch.device) -> None:
    cls_encoder = getattr(model_mod, "cls_encoder", None)
    if cls_encoder is None:
        return
    cls_encoder.device = device
    clip_model = getattr(cls_encoder, "clip_model", None)
    if clip_model is not None:
        cls_encoder.clip_model = clip_model.to(device)


def build_model_direct(cfg, device: torch.device):
    model_type = cfg.model.type
    num_category = len(cfg.training_cfg.train_affordance)
    if model_type == "openad_pn2":
        model_mod = load_openad_submodule("openad_pn2")
        model_cls = model_mod.OpenAD_PN2
        model = model_cls(
            cfg.model,
            num_category,
            normal_channel=cfg.model.get("normal_channel", False),
        )
    elif model_type == "openad_dgcnn":
        model_mod = load_openad_submodule("openad_dgcnn")
        model_cls = model_mod.OpenAD_DGCNN
        model = model_cls(cfg.model, num_category)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    model = model.to(device)
    patch_legacy_class_encoder(model_mod, device)
    return model


def build_dataset_direct(cfg, splits=("train", "val")):
    dataset_mod = importlib.import_module("dataset")
    dataset_cls = dataset_mod.AffordNetDataset
    data_info = cfg.data
    data_root = data_info.data_root
    if_partial = cfg.training_cfg.get("partial", False)
    use_geom_side = data_info.get("use_geom_side", False)
    geom_k = data_info.get("geom_k", 16)
    tc_prior_path = data_info.get("tc_prior_path", None)
    target_affordance = data_info.get("target_affordance", None)
    mock_tc_prior = data_info.get("mock_tc_prior", False)

    dataset_dict = {}
    for split in splits:
        dataset_dict[f"{split}_set"] = dataset_cls(
            data_root,
            split,
            partial=if_partial,
            use_geom_side=use_geom_side,
            geom_k=geom_k,
            tc_prior_path=tc_prior_path,
            target_affordance=target_affordance,
            mock_tc_prior=mock_tc_prior,
        )
    return dataset_dict
