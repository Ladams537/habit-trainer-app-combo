"""Tests for habit streak and strength algorithms (no database needed)."""
from datetime import date, timedelta

from src.modules.habits.service import compute_habit_strength, compute_streaks


class TestComputeStreaks:
    def test_empty_completions(self):
        current, longest = compute_streaks([])
        assert current == 0
        assert longest == 0

    def test_single_day_today(self):
        today = date.today()
        current, longest = compute_streaks([today])
        assert current == 1
        assert longest == 1

    def test_single_day_yesterday(self):
        yesterday = date.today() - timedelta(days=1)
        current, longest = compute_streaks([yesterday])
        assert current == 0  # not today, so current streak is 0
        assert longest == 1

    def test_consecutive_days_including_today(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(5)]
        current, longest = compute_streaks(dates)
        assert current == 5
        assert longest == 5

    def test_gap_in_middle(self):
        today = date.today()
        # Today + yesterday (streak of 2), then gap, then 3 days before
        dates = [
            today,
            today - timedelta(days=1),
            # gap on day -2
            today - timedelta(days=3),
            today - timedelta(days=4),
            today - timedelta(days=5),
        ]
        current, longest = compute_streaks(dates)
        assert current == 2
        assert longest == 3

    def test_streak_ended_yesterday(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(1, 8)]  # 7 days ending yesterday
        current, longest = compute_streaks(dates)
        assert current == 0  # today is missing
        assert longest == 7

    def test_duplicates_handled(self):
        today = date.today()
        dates = [today, today, today - timedelta(days=1)]
        current, longest = compute_streaks(dates)
        assert current == 2
        assert longest == 2


class TestComputeHabitStrength:
    def test_empty_completions(self):
        assert compute_habit_strength([]) == 0.0

    def test_single_completion_today(self):
        strength = compute_habit_strength([date.today()])
        assert 0.06 < strength < 0.08  # approximately alpha

    def test_30_consecutive_days(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(30)]
        strength = compute_habit_strength(dates)
        # After ~30 days, strength should be around 0.87-0.89
        assert 0.85 < strength < 0.92

    def test_strength_decays_after_miss(self):
        today = date.today()
        # 10 consecutive days, then 5 days off
        dates = [today - timedelta(days=i) for i in range(5, 15)]
        strength = compute_habit_strength(dates)
        # Should have decayed during the 5 missed days
        assert strength < 0.5

    def test_perfect_90_days_near_max(self):
        today = date.today()
        dates = [today - timedelta(days=i) for i in range(90)]
        strength = compute_habit_strength(dates)
        # Should be very close to 1.0
        assert strength > 0.98

    def test_strength_always_between_0_and_1(self):
        today = date.today()
        dates = [today - timedelta(days=i * 3) for i in range(30)]  # every 3rd day
        strength = compute_habit_strength(dates)
        assert 0 <= strength <= 1
