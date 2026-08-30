"""
Regression tests for the CandidateRanker scoring defect reported in Section 6.10.

Run:  python -m pytest test_candidate_ranker.py -v
  or: python test_candidate_ranker.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from candidate_ranker import CandidateRanker

# Exactly the keys ResumeMatcher.match_candidates_to_job() emits.
MATCHER_KEYS = ['candidateId', 'candidateName', 'email', 'matchScore', 'skillsMatch',
                'experienceMatch', 'educationMatch', 'semanticMatch',
                'matchedSkills', 'missingSkills', 'breakdown']


def _candidate(v):
    return dict(candidateId='x', candidateName='Test', email='t@example.com',
                matchScore=v, skillsMatch=v, experienceMatch=v,
                educationMatch=v, semanticMatch=v,
                matchedSkills=[], missingSkills=[], breakdown={})


def test_criteria_keys_exist_in_matcher_output():
    """Every ranking criterion must be a key ResumeMatcher actually emits."""
    r = CandidateRanker()
    missing = [c for c in r.ranking_criteria if c not in MATCHER_KEYS]
    assert not missing, f"ranking criteria absent from matcher output: {missing}"


def test_weights_sum_to_one():
    r = CandidateRanker()
    total = sum(r.ranking_criteria.values())
    assert abs(total - 1.0) < 1e-6, f"weights sum to {total}, not 1.0"


def test_perfect_candidate_scores_100_and_is_excellent():
    """The regression that caused the bug: max attainable score was 60."""
    r = CandidateRanker()
    out = r.rank_candidates([_candidate(100.0)])[0]
    assert out['compositeScore'] == 100.0, \
        f"perfect candidate scored {out['compositeScore']}, expected 100.0"
    assert out['tier'] == 'Excellent', f"perfect candidate tiered as {out['tier']}"


def test_zero_candidate_is_below_average():
    r = CandidateRanker()
    out = r.rank_candidates([_candidate(0.0)])[0]
    assert out['compositeScore'] == 0.0
    assert out['tier'] == 'Below Average'


def test_every_tier_is_reachable():
    """No tier boundary may be unattainable under any valid input."""
    r = CandidateRanker()
    seen = {r.rank_candidates([_candidate(v)])[0]['tier']
            for v in (95.0, 75.0, 60.0, 45.0, 10.0)}
    expected = {'Excellent', 'Strong', 'Good', 'Average', 'Below Average'}
    assert seen == expected, f"unreachable tiers: {expected - seen}"


def test_missing_criterion_raises_instead_of_silently_skipping():
    r = CandidateRanker()
    bad = _candidate(100.0)
    del bad['matchScore']
    try:
        r.rank_candidates([bad])
    except KeyError:
        return
    raise AssertionError("a missing ranking criterion was silently ignored")


if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"PASS  {fn.__name__}")
        except Exception as e:
            failed += 1; print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns)-failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
