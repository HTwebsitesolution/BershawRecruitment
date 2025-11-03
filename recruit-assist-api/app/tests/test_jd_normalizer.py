from app.services.jd_normalizer import normalize_jd

def test_normalize_jd_defaults_and_weights():
    jd = normalize_jd(text="We need Node, AWS, SQL")
    assert jd.job.location_policy in {"onsite", "hybrid", "remote"}
    assert len(jd.requirements.must_haves) >= 3
    weights = [m.weight for m in jd.requirements.must_haves]
    assert max(weights) <= 1.0


