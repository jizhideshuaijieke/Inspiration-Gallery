import shutil
import subprocess
import sys
from pathlib import Path

from app.config import settings
from app.service.media_store import get_generated_image_path, get_input_image_path

STYLE_CHECKPOINT_MAP = {
    "vangogh": "style_vangogh_pretrained",
    "ink": "style_wash_pretrained",
    "cezanne": "style_cezanne_prertrained",
    "monet": "style_monet_pretrained",
    "ukiyoe": "style_ukiyoe_pretrained",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_infer_python() -> Path:
    root = _project_root()
    windows_venv = root / "transfer-models" / ".venv" / "Scripts" / "python.exe"
    posix_venv = root / "transfer-models" / ".venv" / "bin" / "python"
    if windows_venv.exists():
        return windows_venv
    if posix_venv.exists():
        return posix_venv
    return Path(sys.executable)


def _runtime_root() -> Path:
    root = _project_root() / "server" / ".runtime"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _logs_dir() -> Path:
    logs = _runtime_root() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def _resolve_checkpoint_file(style_code: str) -> Path:
    model_root = Path(settings.model_root).resolve()
    style_dir_name = STYLE_CHECKPOINT_MAP.get(style_code, f"style_{style_code}_pretrained")
    style_dir = model_root / style_dir_name
    if not style_dir.exists():
        raise RuntimeError(f"未找到风格权重目录: {style_dir}")

    latest = style_dir / "latest_net_G.pth"
    if latest.exists():
        return latest

    pth_files = sorted(style_dir.glob("*.pth"))
    if not pth_files:
        raise RuntimeError(f"风格权重目录中没有 .pth 文件: {style_dir}")
    return pth_files[0]


def _prepare_runtime_checkpoint(task_id: int, checkpoint_file: Path) -> tuple[Path, str]:
    run_name = f"task_{task_id}"
    checkpoints_parent = _runtime_root() / "checkpoints"
    run_ckpt_dir = checkpoints_parent / run_name
    run_ckpt_dir.mkdir(parents=True, exist_ok=True)

    target_ckpt = run_ckpt_dir / "latest_net_G.pth"
    if not target_ckpt.exists():
        try:
            target_ckpt.hardlink_to(checkpoint_file)
        except OSError:
            shutil.copy2(checkpoint_file, target_ckpt)
    return checkpoints_parent, run_name


def _find_generated_image(result_dir: Path) -> Path:
    fake_candidates = sorted(result_dir.glob("*_fake*.png"))
    if fake_candidates:
        return fake_candidates[0]

    all_png = sorted(result_dir.glob("*.png"))
    if all_png:
        return all_png[0]

    raise RuntimeError(f"未找到推理输出图片: {result_dir}")


def run_style_transfer(task_id: int, input_image_url: str, style_code: str) -> None:
    transfer_root = _project_root() / "transfer-models"
    test_script = transfer_root / "test.py"
    if not test_script.exists():
        raise RuntimeError(f"未找到推理脚本: {test_script}")

    input_image_path = get_input_image_path(input_image_url)
    checkpoint_file = _resolve_checkpoint_file(style_code)
    checkpoints_parent, run_name = _prepare_runtime_checkpoint(task_id, checkpoint_file)

    runtime_root = _runtime_root()
    input_dir = runtime_root / "inputs" / run_name
    input_dir.mkdir(parents=True, exist_ok=True)
    runtime_input = input_dir / f"input{input_image_path.suffix.lower()}"
    shutil.copy2(input_image_path, runtime_input)

    results_dir = runtime_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(_resolve_infer_python()),
        "test.py",
        "--dataroot",
        str(input_dir),
        "--name",
        run_name,
        "--model",
        "test",
        "--no_dropout",
        "--num_test",
        "1",
        "--checkpoints_dir",
        str(checkpoints_parent),
        "--results_dir",
        str(results_dir),
        "--preprocess",
        "none",
    ]

    proc = subprocess.run(
        cmd,
        cwd=str(transfer_root),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        log_path = _logs_dir() / f"task-{task_id}.log"
        with log_path.open("w", encoding="utf-8") as f:
            f.write("Command:\n")
            f.write(" ".join(cmd))
            f.write("\n\nSTDOUT:\n")
            f.write(proc.stdout or "")
            f.write("\n\nSTDERR:\n")
            f.write(proc.stderr or "")
        raise RuntimeError(f"模型推理失败，详见日志: {log_path}")

    image_dir = results_dir / run_name / "test_latest" / "images"
    generated_src = _find_generated_image(image_dir)

    output_path = get_generated_image_path(task_id)
    shutil.copy2(generated_src, output_path)
