"""Ensaio E1: reprodução do Blue B Call Index do MBARI (BENCH_CRITERIA v0.3.1, Seção 9).

Segue o processamento em lote do notebook do MBARI, conforme a referência congelada em
lab/bench/e1_reference.json:
  - arquivo diário de 2 kHz do bucket público pacific-sound-2khz (AWS Open Data, CC BY 4.0);
  - tensão escalada por 3; segmentos de 60 s;
  - Welch com janela Hann de 2000 amostras e nfft = 2000 (resolução de 1 Hz), sobreposição padrão do SciPy
    (o notebook não especifica noverlap);
  - PSD em dB calibrado: 10*log10(psd) - sens;
  - CI por minuto = média(PSD em 43 e 44 Hz) / média(PSD em 37 e 50 Hz), razão entre níveis em dB;
  - média diária só com minutos com menos de 1% de amostras ausentes (amostras exatamente iguais a zero).
Critério: diferença relativa <= 2% nas médias diárias de 01, 11 e 22/11/2016.

Uso: python lab/bench/e1_mbari.py [--days 2016-11-01,2016-11-11,2016-11-22] [--keep] [--wav-dir DIR]
O áudio bruto não é versionado; o resultado vai para lab/bench/results/e1/E1.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import scipy
import soundfile as sf
from scipy import signal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REF = json.loads((HERE / "e1_reference.json").read_text(encoding="utf-8"))
BUCKET = "https://pacific-sound-2khz.s3.amazonaws.com"
CRITERION_DAYS = ["2016-11-01", "2016-11-11", "2016-11-22"]


def sensitivity(day: str) -> float:
    return REF["sensitivity_db_re_v_per_upa"]["before_2017-06-14" if day < "2017-06-14" else "from_2017-06-14"]


def find_key(day: str) -> str:
    """Localiza o arquivo do dia listando o prefixo do mês no bucket público (sem credenciais)."""
    y, m, d = day.split("-")
    url = f"{BUCKET}/?list-type=2&prefix={y}/{m}/"
    with urllib.request.urlopen(url, timeout=60) as r:
        root = ET.fromstring(r.read())
    ns = {"s3": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
    keys = [k.text for k in root.iter(("{%s}Key" % ns["s3"]) if ns else "Key")]
    stamp = f"{y}{m}{d}"
    match = [k for k in keys if stamp in k and k.lower().endswith(".wav")]
    if not match:
        raise FileNotFoundError(f"nenhum WAV para {day} em {url}")
    return sorted(match)[0]


def download(key: str, dest: Path) -> str:
    h = hashlib.sha256()
    with urllib.request.urlopen(f"{BUCKET}/{key}", timeout=600) as r, dest.open("wb") as f:
        while chunk := r.read(1 << 22):
            f.write(chunk)
            h.update(chunk)
    return h.hexdigest()


def daily_ci(path: Path, day: str) -> dict:
    fs_expected = 2000
    sens = sensitivity(day)
    peak, bg = REF["peak_hz"], REF["background_hz"]
    seg = REF["segment_s"]
    ci_min, missing = [], []
    with sf.SoundFile(str(path)) as snd:
        info = {"samplerate": snd.samplerate, "channels": snd.channels, "frames": snd.frames,
                "duration_s": snd.frames / snd.samplerate, "subtype": snd.subtype}
        assert snd.samplerate == fs_expected, f"taxa {snd.samplerate} != {fs_expected}"
        n = seg * snd.samplerate
        while True:
            v = snd.read(frames=n, dtype="float64", always_2d=False)
            if v.ndim > 1:
                v = v[:, 0]
            if v.size < n:
                break
            miss = float(np.mean(v == 0.0))
            v = v * REF["voltage_scale"]
            f, p = signal.welch(v, fs=snd.samplerate, window="hann", nperseg=REF["welch"]["nperseg"], nfft=REF["welch"]["nfft"])
            with np.errstate(divide="ignore"):
                pdb = 10 * np.log10(p) - sens
            idx = lambda hz: int(np.argmin(np.abs(f - hz)))  # noqa: E731
            pk = np.mean([pdb[idx(h)] for h in peak])
            bk = np.mean([pdb[idx(h)] for h in bg])
            ci_min.append(float(pk / bk) if np.isfinite(pk) and np.isfinite(bk) and bk != 0 else float("nan"))
            missing.append(miss)
    ci = np.array(ci_min)
    ok = (np.array(missing) < 0.01) & np.isfinite(ci)
    return {"file_info": info, "minutes": int(ci.size), "valid_minutes": int(ok.sum()),
            "excluded_minutes": int((~ok).sum()), "daily_mean_ci": float(np.mean(ci[ok])) if ok.any() else None,
            "sensitivity_db": sens}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", default=",".join(CRITERION_DAYS))
    ap.add_argument("--keep", action="store_true", help="manter os WAV baixados")
    ap.add_argument("--wav-dir", default=None)
    a = ap.parse_args()
    wav_dir = Path(a.wav_dir) if a.wav_dir else Path(tempfile.mkdtemp(prefix="mbari_"))
    wav_dir.mkdir(parents=True, exist_ok=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "desconhecido"
    out = {"experiment": "E1", "criteria_version": "0.3.1", "commit": commit,
           "date_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "env": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                   "soundfile": sf.__version__, "platform": platform.platform()},
           "source": BUCKET, "license": "CC BY 4.0 (MBARI)", "tolerance_relative": REF["tolerance_relative"],
           "noverlap": "padrão do SciPy (nperseg//2), pois o notebook não especifica", "days": {}}
    for day in a.days.split(","):
        key = find_key(day)
        path = wav_dir / Path(key).name
        sha = download(key, path) if not path.exists() else hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{day}: {key} sha256={sha[:12]}", flush=True)
        r = daily_ci(path, day)
        ref = REF["daily_mean_ci"].get(day)
        rel = abs(r["daily_mean_ci"] - ref) / ref if (ref and r["daily_mean_ci"]) else None
        r.update({"key": key, "sha256": sha, "accessed_utc": out["date_utc"], "reference_ci": ref,
                  "relative_difference": rel, "criterion_day": day in CRITERION_DAYS,
                  "passed": (rel is not None and rel <= REF["tolerance_relative"]) if day in CRITERION_DAYS else None})
        out["days"][day] = r
        print(f"  CI diário={r['daily_mean_ci']:.6f} ref={ref} dif_rel={rel} minutos válidos={r['valid_minutes']}/{r['minutes']}", flush=True)
        if not a.keep:
            path.unlink(missing_ok=True)
    crit = [out["days"][d]["passed"] for d in CRITERION_DAYS if d in out["days"]]
    out["passed"] = bool(crit) and len(crit) == len(CRITERION_DAYS) and all(crit)
    res = HERE / "results" / "e1"
    res.mkdir(parents=True, exist_ok=True)
    (res / "E1.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"E1 passed={out['passed']}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
