"""FSRS (Free Spaced Repetition Scheduler) — pure functions, no DB dependencies."""

from datetime import datetime, timedelta, timezone


def compute_retrievability(stability: float, days_elapsed: float) -> float:
    """Compute memory retrievability R given stability S and elapsed time t.

    R = (1 + t / (9 * S))^(-1)
    Returns a value between 0 and 1.
    """
    if stability <= 0 or days_elapsed < 0:
        return 1.0
    return (1 + days_elapsed / (9 * stability)) ** -1


def compute_next_review_date(
    last_review: datetime, stability: float, threshold: float = 0.9
) -> datetime:
    """Compute when retrievability drops below the threshold.

    Solving R = threshold for t:  t = 9 * S * (threshold^(-1) - 1)
    """
    if stability <= 0:
        return last_review + timedelta(days=1)
    interval_days = 9 * stability * (threshold**-1 - 1)
    interval_days = max(interval_days, 0.5)  # minimum half-day
    return last_review + timedelta(days=interval_days)


def update_fsrs_params(
    difficulty: float,
    stability: float,
    quality: int,
) -> tuple[float, float, datetime]:
    """Update FSRS parameters after a review.

    Args:
        difficulty: current difficulty (1-10 scale)
        stability: current stability in days
        quality: rating 1-5

    Returns:
        (new_difficulty, new_stability, next_review_date)
    """
    # Adjust difficulty: moves toward the quality-implied difficulty
    new_d = difficulty + (3 - quality) * 0.3
    new_d = max(1.0, min(10.0, new_d))

    now = datetime.now(timezone.utc)

    if quality >= 3:
        # Successful recall — grow stability
        # Growth factor decreases with difficulty
        growth = 2.5 * (1 - (new_d - 1) / 9 * 0.5)
        growth = max(1.1, growth)
        new_s = stability * growth
    elif quality == 2:
        # Lapse — halve stability
        new_s = stability * 0.5
        new_s = max(0.5, new_s)
    else:
        # Complete lapse — reset
        new_s = 1.0

    next_review = compute_next_review_date(now, new_s)

    return (round(new_d, 2), round(new_s, 2), next_review)


def is_due_for_review(next_review_date: datetime | None) -> bool:
    """Check if a sub-skill is due for review (i.e. next_review_date <= now)."""
    if next_review_date is None:
        return True  # never reviewed = always due
    return datetime.now(timezone.utc) >= next_review_date
