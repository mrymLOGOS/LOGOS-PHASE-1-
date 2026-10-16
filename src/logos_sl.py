"""
بنیاد LOGOS (Logos Foundation)
شاخه: LOGOS-SL — Supervisory Layer for Epistemic Uncertainty

فاز ۱: مانیتور ناهنجاری + عدم‌قطعیت + تصمیم
"""

from __future__ import annotations

from typing import Dict, Any, Union
import numpy as np


def img_to_compact_feat(img: Union[np.ndarray, Any]) -> np.ndarray:
    """
    فشرده‌سازی تصویر به ویژگی کم‌بُعد برای LOGOS-SL.
    ورودی: (C,H,W) یا (H,W,C) — معمولاً 3x32x32
    خروجی: mean/std/min/max هر کانال + میانگین بلوک‌های 8x8
    """
    x = img.numpy() if hasattr(img, "numpy") else np.asarray(img, dtype=np.float64)
    if x.ndim != 3:
        raise ValueError("img must be 3D (C,H,W) or (H,W,C)")
    # اگر HWC بود به CHW
    if x.shape[0] not in (1, 3) and x.shape[-1] in (1, 3):
        x = np.transpose(x, (2, 0, 1))
    c, h, w = x.shape
    block = 8
    feats = []
    for ch_i in range(c):
        ch = x[ch_i]
        feats.extend([float(ch.mean()), float(ch.std()), float(ch.min()), float(ch.max())])
        for i in range(0, h, block):
            for j in range(0, w, block):
                feats.append(float(ch[i : i + block, j : j + block].mean()))
    return np.asarray(feats, dtype=np.float64)


class LogosSLMonitor:
    """مانیتور نظارتی LOGOS-SL"""

    def __init__(
        self,
        anomaly_threshold: float = 0.50,
        uncertainty_threshold: float = 0.50,
        safe_stop_anomaly: float = 0.75,
    ):
        self.anomaly_threshold = float(anomaly_threshold)
        self.uncertainty_threshold = float(uncertainty_threshold)
        self.safe_stop_anomaly = float(safe_stop_anomaly)
        self.mu = None
        self.sigma = None

    def fit(self, X_normal: np.ndarray) -> "LogosSLMonitor":
        X_normal = np.asarray(X_normal, dtype=np.float64)
        if X_normal.ndim != 2 or len(X_normal) < 2:
            raise ValueError("X_normal must be 2D with at least 2 rows")
        self.mu = X_normal.mean(axis=0)
        self.sigma = X_normal.std(axis=0) + 1e-6
        return self

    def _scores(self, X: np.ndarray):
        if self.mu is None or self.sigma is None:
            raise RuntimeError("Call fit() before predict()")
        X = np.asarray(X, dtype=np.float64)
        z = np.abs((X - self.mu) / self.sigma)
        anomaly = np.clip(z.mean(axis=1) / 3.0, 0.0, 1.0)
        uncertainty = np.clip(z.std(axis=1) / 2.0, 0.0, 1.0)
        return anomaly, uncertainty

    def predict(self, X: np.ndarray) -> Dict[str, Any]:
        anomaly, uncertainty = self._scores(X)
        decisions = []
        for a, u in zip(anomaly, uncertainty):
            if a >= self.anomaly_threshold or u >= self.uncertainty_threshold:
                decisions.append(
                    "SAFE_STOP" if a >= self.safe_stop_anomaly else "CAUTION"
                )
            else:
                decisions.append("OK")
        return {
            "anomaly_score": anomaly,
            "uncertainty": uncertainty,
            "decision": np.array(decisions, dtype=object),
        }


def baseline_predict(
    confidences: np.ndarray,
    conf_threshold: float = 0.7,
) -> Dict[str, Any]:
    confidences = np.asarray(confidences, dtype=np.float64)
    decisions = np.where(confidences >= conf_threshold, "OK", "CAUTION")
    return {
        "anomaly_score": 1.0 - confidences,
        "decision": decisions,
    }


def binary_ood_flags(decisions: np.ndarray) -> np.ndarray:
    return np.array([d != "OK" for d in decisions], dtype=bool)


def eval_ood(y_true_ood: np.ndarray, flagged: np.ndarray) -> Dict[str, float]:
    y_true_ood = np.asarray(y_true_ood, dtype=bool)
    flagged = np.asarray(flagged, dtype=bool)
    tp = int(np.sum(y_true_ood & flagged))
    fn = int(np.sum(y_true_ood & ~flagged))
    fp = int(np.sum(~y_true_ood & flagged))
    tn = int(np.sum(~y_true_ood & ~flagged))
    tpr = tp / (tp + fn + 1e-9)
    fpr = fp / (fp + tn + 1e-9)
    return {
        "TPR": float(tpr),
        "FPR": float(fpr),
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        }

## وضعیت فاز ۲ تا اینجا (16/10/2026)
- پیش‌فرض پژوهشی: fit_adaptive p95
- آزمایش ۴ و ۵: TPR≈0.95 ، FPR≈0.085 روی CIFAR فشرده
- API رسمی fit_adaptive در logos_sl.py تأیید شد
- هدف بعدی: کاهش FPR با حفظ TPR قابل قبول
