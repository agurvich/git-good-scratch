from wb_analytics.poverty_calc import poverty_rate, gini_coefficient


def test_poverty_rate_basic(sample_incomes):
    rate = poverty_rate(sample_incomes, line=2.0)
    assert 0 <= rate <= 1


def test_gini_coefficient_nonzero_population(sample_incomes):
    gini = gini_coefficient(sample_incomes, population=len(sample_incomes))
    assert gini is not None


def test_gini_equal_incomes_is_zero_when_population_differs():
    # Survey rows are often weighted: 3 observations can stand for 6 people.
    # Equal incomes mean perfect equality, whatever the population is.
    assert gini_coefficient([1, 1, 1], population=6) == 0
