"""تست سریع LOGOS-SL — 18/10/2026"""
import sys
sys.path.insert(0, "src")

from logos_sl import logos_sl_self_test, __version__

def test_self_test_ok():
    r = logos_sl_self_test()
    assert r["ok"] is True
    assert r["save_load"] is True
    assert r["TPR"] >= 0.8
    assert r["FPR"] <= 0.2

def test_version():
    assert __version__ >= "0.2.0"

if __name__ == "__main__":
    test_version()
    test_self_test_ok()
    print("بنیاد LOGOS | tests OK | 18/10/2026 01:00 | version", __version__)
