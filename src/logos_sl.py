
"""
بنیاد LOGOS (Logos Foundation)
شاخه: LOGOS-SL — Supervisory Layer for Epistemic Uncertainty
"""
# Checkpoint A (فاز ۲): fit_adaptive p95 + OR | مرجع آزمایش‌های ۴–۹
# Checkpoint B (17/10/2026): p95+OR+safe_stop0.75 | save/load | self_test | get_config

from __future__ import annotations

from typing import Dict, Any, Union
import numpy as np


def img_to_compact_feat(img: Union[np.ndarray, Any]) -> np.ndarray:
    x = img.numpy() if hasattr(img, "numpy") else np.asarray(img, dtype=np.float64)
    if x.ndim != 3:
        raise ValueError("img must be 3D (C,H,W) or (H,W,C)")
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

    def fit_adaptive(
        self,
        X_normal: np.ndarray,
        percentile_anom: float = 95.0,
        percentile_unc: float = 95.0,
    ) -> "LogosSLMonitor":
        """فاز ۲: آستانه از صدک امتیازهای دادهٔ عادی (پیش‌فرض p95)."""
        self.fit(X_normal)
        z = np.abs((X_normal - self.mu) / self.sigma)
        anom = np.clip(z.mean(axis=1) / 3.0, 0.0, 1.0)
        unc = np.clip(z.std(axis=1) / 2.0, 0.0, 1.0)
        self.anomaly_threshold = float(np.percentile(anom, percentile_anom))
        self.uncertainty_threshold = float(np.percentile(unc, percentile_unc))
        return self
    def save(self, path: str) -> None:
        """ذخیره پارامترهای fit‌شده LOGOS-SL"""
        if self.mu is None or self.sigma is None:
            raise RuntimeError("Nothing to save; call fit or fit_adaptive first")
        np.savez(
            path,
            mu=self.mu,
            sigma=self.sigma,
            anomaly_threshold=np.array([self.anomaly_threshold]),
            uncertainty_threshold=np.array([self.uncertainty_threshold]),
            safe_stop_anomaly=np.array([self.safe_stop_anomaly]),
        )

    def load(self, path: str) -> "LogosSLMonitor":
        """بارگذاری پارامترهای ذخیره‌شده"""
        data = np.load(path)
        self.mu = data["mu"]
        self.sigma = data["sigma"]
        self.anomaly_threshold = float(data["anomaly_threshold"][0])
        self.uncertainty_threshold = float(data["uncertainty_threshold"][0])
        self.safe_stop_anomaly = float(data["safe_stop_anomaly"][0])
        return self

        def get_config(self) -> dict:
        return {
            "anomaly_threshold": self.anomaly_threshold,
            "uncertainty_threshold": self.uncertainty_threshold,
            "safe_stop_anomaly": self.safe_stop_anomaly,
            "fitted": self.mu is not None,
            "feature_dim": None if self.mu is None else int(self.mu.shape[0]),
            "checkpoint": "B",
            "date": "17/10/2026",
        }
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


def baseline_predict(confidences: np.ndarray, conf_threshold: float = 0.7) -> Dict[str, Any]:
    confidences = np.asarray(confidences, dtype=np.float64)
    decisions = np.where(confidences >= conf_threshold, "OK", "CAUTION")
    return {"anomaly_score": 1.0 - confidences, "decision": decisions}


def binary_ood_flags(decisions: np.ndarray) -> np.ndarray:
    return np.array([d != "OK" for d in decisions], dtype=bool)


def eval_ood(y_true_ood: np.ndarray, flagged: np.ndarray) -> Dict[str, float]:
    y_true_ood = np.asarray(y_true_ood, dtype=bool)
    flagged = np.asarray(flagged, dtype=bool)
    tp = int(np.sum(y_true_ood & flagged))
    fn = int(np.sum(y_true_ood & ~flagged))
    fp = int(np.sum(~y_true_ood & flagged))
    tn = int(np.sum(~y_true_ood & ~flagged))
    return {
        "TPR": float(tp / (tp + fn + 1e-9)),
        "FPR": float(fp / (fp + tn + 1e-9)),
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

def logos_sl_self_test() -> dict:
    """خودآزمایی سریع بدون دیتاست سنگین — 17/10/2026"""
    rng = np.random.default_rng(42)
    Xn = rng.normal(0, 1, size=(300, 32))
    Xo = rng.normal(2.5, 1.5, size=(100, 32))
    m = LogosSLMonitor().fit_adaptive(Xn, 95.0, 95.0)
    fpr = float(np.mean(m.predict(Xn)["decision"] != "OK"))
    tpr = float(np.mean(m.predict(Xo)["decision"] != "OK"))
    m.save("_logos_sl_self_test.npz")
    m2 = LogosSLMonitor().load("_logos_sl_self_test.npz")
    same = bool(
        np.allclose(m.predict(Xo)["anomaly_score"], m2.predict(Xo)["anomaly_score"])
    )
    ok = (tpr > 0.8) and (fpr < 0.2) and same
    return {"ok": ok, "TPR": round(tpr, 3), "FPR": round(fpr, 3), "save_load": same}


if __name__ == "__main__":
    print("بنیاد LOGOS | LOGOS-SL self-test")
    print(logos_sl_self_test())

def build_status_report(monitor: LogosSLMonitor | None = None) -> dict:
    """گزارش وضعیت استاندارد بنیاد LOGOS — LOGOS-SL"""
    st = logos_sl_self_test()
    cfg = monitor.get_config() if monitor is not None else {
        "checkpoint": "B",
        "date": "17/10/2026",
        "fitted": False,
    }
    return {
        "project": "LOGOS-SL",
        "date": "17/10/2026",
        "checkpoint": "B",
        "config": cfg,
        "self_test": st,
}


