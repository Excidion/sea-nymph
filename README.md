# sea_nymph
A matplotlib-style Python library for generating Mermaid diagrams


## Usage
```python
from sea_nymph import XYChart

months = ["Jan", "Feb", "Mar", "Apr"]
fig = XYChart()
fig.bar(months, [10, 40, 30, 50])
fig.line(months, [15, 35, 25, 45])
fig.xlabel("Month")
fig.ylabel("Revenue (k)")
fig.ylim(0, 60)
fig.title("Sales 2024")
```
results in the following mermaid chart:
```mermaid
xychart-beta
    title "Sales 2024"
    x-axis "Month" [Jan, Feb, Mar, Apr]
    y-axis "Revenue (k)" 0 --> 60
    bar [10, 40, 30, 50]
    line [15, 35, 25, 45]
```

