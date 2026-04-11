#!/usr/bin/env python3
"""
TC-Prior 硬件性能与计算效率评测脚本 (Hardware Profiling)
测试内容：
1. Params (参数量，精确到 M)
2. FLOPs / MACs (浮点运算次数，精确到 G)
3. Latency & FPS (推理延迟与帧率，包含 Warm-up 和多次平均)

支持设备：CPU (Macbook/Jetson/Laptop) 或 GPU (CUDA)
用法：
  python scripts/profile_efficiency.py --device cpu
  python scripts/profile_efficiency.py --device cuda
"""

import os
import sys
import time
import argparse
import importlib.util
import types
from pathlib import Path
import numpy as np
import torch
import warnings

# 禁用库警告以保持输出清爽
warnings.filterwarnings('ignore')

try:
    from thop import profile, clever_format
except ImportError:
    profile = None
    clever_format = None

BASE = os.environ.get(
    "OPENAD_BASE", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Open-Vocabulary-Affordance-Detection-in-3D-Point-Clouds-main")
)
BASE = os.path.abspath(BASE)


def maybe_add_clip_root() -> None:
    candidates = []
    env_root = os.environ.get("OPENAI_CLIP_ROOT", "")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    base = Path(BASE)
    candidates.extend(
        [
            base / "openai_CLIP",
            base.parent / "openai_CLIP",
            base.parent.parent / "openai_CLIP",
        ]
    )

    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "clip" / "__init__.py").is_file():
            sys.path.insert(0, str(candidate))
            os.environ.setdefault("OPENAI_CLIP_ROOT", str(candidate))
            return


maybe_add_clip_root()
sys.path.insert(0, BASE)
OPENAD_MODELS_DIR = Path(BASE) / "models"
OPENAD_MODEL_PACKAGE = "affordbench_runtime_openad_models"


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
        if isinstance(module, torch.nn.BatchNorm2d) or isinstance(module, torch.nn.BatchNorm1d):
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
        raise ValueError(f"Unsupported model type for profiling: {model_type}")
    model = model.to(device)
    patch_legacy_class_encoder(model_mod, device)
    return model


def measure_inference_speed(model, dummy_input, dummy_classes, device_str, num_runs=100, num_warmups=20):
    """测量推理延迟和FPS"""
    print(f"[{device_str.upper()}] Warming up for {num_warmups} iterations...")
    
    # Warm up
    with torch.no_grad():
        for _ in range(num_warmups):
            _ = model(dummy_input, dummy_classes)
            
    if 'cuda' in device_str:
        torch.cuda.synchronize()
        
    print(f"[{device_str.upper()}] Running {num_runs} iterations for benchmark...")
    
    latencies = []
    with torch.no_grad():
        for _ in range(num_runs):
            start_time = time.perf_counter()
            _ = model(dummy_input, dummy_classes)
            if 'cuda' in device_str:
                torch.cuda.synchronize()
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000) # 转换为毫秒
            
    avg_latency = np.mean(latencies)
    std_latency = np.std(latencies)
    fps = 1000.0 / avg_latency if avg_latency > 0 else 0
    
    return avg_latency, std_latency, fps


def main():
    parser = argparse.ArgumentParser(description="Profile TC-Prior efficiency")
    parser.add_argument(
        "--config",
        type=str,
        default=os.environ.get("OPENAD_CONFIG", "config/openad_pn2/full_shape_cfg.py"),
        help="Config path relative to OPENAD_BASE or absolute path.",
    )
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda", "mps"], help="Device to run profiling on")
    parser.add_argument("--batch_size", type=int, default=1, help="Batch size for profiling (default: 1 for edge inference)")
    parser.add_argument("--num_points", type=int, default=2048, help="Number of points per point cloud")
    parser.add_argument("--num_runs", type=int, default=100, help="Number of timed forward passes")
    parser.add_argument("--num_warmups", type=int, default=20, help="Number of warmup forward passes")
    args = parser.parse_args()

    device = torch.device(args.device)
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("CUDA is not available. Falling back to CPU.")
        device = torch.device('cpu')
        args.device = 'cpu'

    restore_cuda_is_available = None
    if args.device == 'cpu':
        restore_cuda_is_available = torch.cuda.is_available
        torch.cuda.is_available = lambda: False

    restore_clip_load = None
    if args.device == 'cpu':
        _, restore_clip_load = force_cpu_clip_load()

    print(f"\n{'='*50}")
    print(f" TC-Prior Hardware Profiling (Device: {args.device.upper()})")
    print(f"{'='*50}")

    # 1. 构造模型
    print("Building model...")
    config_path = args.config if os.path.isabs(args.config) else os.path.join(BASE, args.config)
    original_utils = install_config_utils_shim()
    try:
        from gorilla.config import Config
        cfg = Config.fromfile(config_path)
    finally:
        restore_config_utils_shim(original_utils)
        
    try:
        # 修改配置以适应单机无 GPU 环境下构建模型
        if args.device == 'cpu':
            cfg.training_cfg.gpu = ""
        model = build_model_direct(cfg, device)
        model.eval()
    finally:
        if restore_clip_load is not None:
            import clip as clip_pkg

            clip_pkg.load = restore_clip_load
        if restore_cuda_is_available is not None:
            torch.cuda.is_available = restore_cuda_is_available

    # 2. 构造 Dummy Input
    # Point cloud 格式: (B, 3, N)
    dummy_pc = torch.randn(args.batch_size, 3, args.num_points).to(device)
    dummy_classes = ["grasp"] * args.batch_size

    # 3. 测量 Params 和 FLOPs
    print("\n[1] Architecture Complexity:")
    params_m = None
    flops_g = None
    if profile is None or clever_format is None:
        total_params = sum(p.numel() for p in model.parameters())
        params_m = total_params / 1e6
        print("  THOP not installed; skipping FLOPs/MACs calculation.")
        print(f"  Total Parameters : {params_m:.2f} M")
    else:
        # thop 对复杂的 dict/list 输入支持不好，我们通过包装一个 dummy 模块来测主干的 FLOPs
        try:
            class ModelWrapper(torch.nn.Module):
                def __init__(self, m):
                    super().__init__()
                    self.m = m
                def forward(self, x):
                    return self.m(x, dummy_classes)
                    
            wrapped_model = ModelWrapper(model)
            macs, params = profile(wrapped_model, inputs=(dummy_pc,), verbose=False)
            macs_str, params_str = clever_format([macs, params], "%.2f")
            
            # MACs * 2 ≈ FLOPs
            flops_g = (macs * 2) / 1e9
            params_m = params / 1e6
            
            print(f"  Total Parameters : {params_m:.2f} M")
            print(f"  MACs             : {macs_str}")
            print(f"  FLOPs (approx)   : {flops_g:.2f} GFLOPs")
        except Exception as e:
            print(f"  FLOPs profiling error: {e}")
            # 备选统计方法
            total_params = sum(p.numel() for p in model.parameters())
            params_m = total_params / 1e6
            print(f"  Total Parameters : {params_m:.2f} M")

    # 4. 测量 Latency 和 FPS
    print(f"\n[2] Inference Speed (Batch={args.batch_size}, Points={args.num_points}):")
    avg_lat, std_lat, fps = measure_inference_speed(
        model,
        dummy_pc,
        dummy_classes,
        args.device,
        num_runs=args.num_runs,
        num_warmups=args.num_warmups,
    )
    
    print(f"  Latency : {avg_lat:.2f} ± {std_lat:.2f} ms / frame")
    print(f"  FPS     : {fps:.2f} frames / sec")
    
    print(f"\n{'='*50}")
    print("Copy this format to your paper (Table 5):")
    flops_str = f"{flops_g:.2f}G" if flops_g is not None else "n/a"
    print(f"Params: {params_m:.2f}M | FLOPs: {flops_str} | FPS ({args.device.upper()}): {fps:.1f}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
