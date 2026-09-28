"""Print a one-line poverty summary for a CSV file with an `income` column."""
import csv
import os
import sys

from wb_analytics.poverty_calc import POVERTY_LINE_USD_PPP, poverty_rate


def summarise( path,line = POVERTY_LINE_USD_PPP ):
    with open(path) as f:
        incomes=[float(row["income"]) for row in csv.DictReader(f)]
    rate=poverty_rate(incomes,line=line)
    return f"{len(incomes)} people, {rate:.1%} below ${line:.2f} a day"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: python scripts/summarise_poverty.py INCOMES.csv")
    print(summarise(sys.argv[1]))
