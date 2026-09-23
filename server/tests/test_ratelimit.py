import pytest

from ratelimit import SlidingWindowLimiter


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


def test_allows_up_to_the_limit_then_reports_retry_after(clock):
    limiter = SlidingWindowLimiter(limit=3, window_seconds=60, clock=clock)

    assert [limiter.hit("ip") for _ in range(3)] == [0, 0, 0]
    clock.now += 20
    assert limiter.hit("ip") == pytest.approx(40)


def test_window_slides(clock):
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60, clock=clock)
    limiter.hit("ip")
    clock.now += 30
    limiter.hit("ip")

    clock.now += 30  # first hit is now exactly one window old
    assert limiter.hit("ip") == 0
    assert limiter.hit("ip") == pytest.approx(30)


def test_denied_hits_are_not_counted(clock):
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=clock)
    limiter.hit("ip")
    for _ in range(5):
        assert limiter.hit("ip") > 0

    clock.now += 60
    assert limiter.hit("ip") == 0


def test_keys_are_independent(clock):
    limiter = SlidingWindowLimiter(limit=1, window_seconds=60, clock=clock)

    assert limiter.hit("a") == 0
    assert limiter.hit("b") == 0
    assert limiter.hit("a") > 0


def test_daily_window(clock):
    limiter = SlidingWindowLimiter(limit=60, window_seconds=86_400, clock=clock)
    for _ in range(60):
        assert limiter.hit("ip") == 0

    clock.now += 3_600
    assert limiter.hit("ip") == pytest.approx(82_800)


def test_stale_keys_are_swept(clock):
    limiter = SlidingWindowLimiter(limit=5, window_seconds=60, clock=clock, sweep_every=3)
    limiter.hit("a")
    limiter.hit("b")
    clock.now += 61

    limiter.hit("c")  # third hit triggers a sweep

    assert set(limiter._hits) == {"c"}


def test_a_limit_of_zero_refuses_instead_of_crashing():
    """RATE_PER_MINUTE=0 is a way to switch the endpoint off, not a way to 500 every request."""
    limiter = SlidingWindowLimiter(limit=0, window_seconds=60)

    assert limiter.hit("ip") == 60
