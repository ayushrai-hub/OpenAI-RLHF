# Create a list of (year, title, sales_millions)

games = [
    (2007, "Assassin's Creed", 8.0),
    (2009, "Assassin's Creed II", 9.0),
    (2010, "Assassin's Creed: Brotherhood", 7.20),
    (2011, "Assassin's Creed: Revelations", 7.0),
    (2012, "Assassin's Creed III", 12.0),
    (2013, "Assassin's Creed IV: Black Flag", 15.0),
    (2014, "Assassin's Creed Unity", 10.0),
    (2017, "Assassin's Creed Origins", 10.0),
    (2018, "Assassin's Creed Odyssey", 10.0),
]

# total span of years from first (2007) to including Mirage (2023)
years_span = 2023 - 2007 + 1  # inclusive

total_sales = sum(g[2] for g in games)
avg_sales_per_year = total_sales / years_span

# Find year with highest sales
max_game = max(games, key=lambda g: g[2])  # by sales
max_year, max_title, max_sales = max_game

print("Total sales:", total_sales)
print("Years span:", years_span)
print("Average annual sales:", avg_sales_per_year)
print("Highest sales year:", max_year, "with game:", max_title, "selling", max_sales)

