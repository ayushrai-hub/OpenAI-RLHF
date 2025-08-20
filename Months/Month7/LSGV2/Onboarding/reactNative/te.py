import math
import requests

# We will fetch up to 1000 (max 10 pages of 100). Without auth because not possible.

import json

def get_repo_stats(hook):
    base = "https://api.github.com/search/repositories"
    query = f"react-native {hook} in:readme,description,name"
    per_page = 100
    repos = []
    # first request to get total count and number of pages
    params = dict(q=query, per_page=per_page, page=1)
    resp = requests.get(base, params=params, headers={'Accept': 'application/vnd.github.v3+json'})
    data = resp.json()
    total = data['total_count']
    # compute pages (max 10)
    max_pages = min(10, math.ceil(total / per_page))
    # gather items from pages
    repos.extend(data['items'])
    for page in range(2, max_pages+1):
        params['page'] = page
        resp = requests.get(base, params=params, headers={'Accept': 'application/vnd.github.v3+json'})
        data = resp.json()
        repos.extend(data['items'])
    # dedup by full_name (should not duplicate across pages)
    unique = {}
    for r in repos:
        full = r['full_name']
        unique[full] = r
    # stats
    star_sum = sum(r['stargazers_count'] for r in unique.values())
    return total, star_sum, len(unique)

# test for useState
print(get_repo_stats('useState'))
