import pytest

from wb_analytics.poverty_calc import poverty_rate


def test_poverty_rate_empty_list_raises_clear_error():
    with pytest.raises(ValueError, match="empty income list"):
        poverty_rate([])


def test_poverty_rate_counts_share_below_line():
    assert poverty_rate([1.0, 2.0, 3.0, 4.0], line=2.5) == 0.5
