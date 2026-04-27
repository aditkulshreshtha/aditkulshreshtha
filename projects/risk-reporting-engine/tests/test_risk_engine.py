from src.risk_engine import Risk


def test_risk_scoring():
    r = Risk('R1','Test','Security',4,5,'Missing','Owner','2026-01-01')
    assert r.score == 20
    assert r.severity == 'Critical'
