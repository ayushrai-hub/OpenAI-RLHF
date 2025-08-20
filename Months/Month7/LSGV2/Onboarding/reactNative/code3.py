import requests
import time

def search_react_native_hooks(api_token):
    # List of hooks to analyze
    hooks = [
        # React core hooks commonly used in React Native
        "useState",
        "useEffect",
        "useContext",
        "useReducer",
        "useCallback",
        "useMemo",
        "useRef",
        
        # React Native specific hooks
        "useWindowDimensions",
        "useSafeAreaInsets",
        "useColorScheme",
        "useAppState",
        
        # React Navigation hooks
        "useNavigation",
        "useRoute",
        "useFocusEffect",
        
        # Popular community hooks
        "useBackHandler",
        "useAnimatedStyle",
        "useSharedValue",
        "useTranslation",
        "useFonts"
    ]
    
    headers = {
        "Authorization": f"token {api_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    hook_stats = {}
    

    for hook in hooks:
        print(f"Analyzing {hook} across GitHub repositories...")
        
        # Search query to find React Native code using this hook across all public repos
        query = f'"{hook}" language:javascript language:typescript "react-native"'
        url = "https://api.github.com/search/code"
        
        repositories = {}
        
        # We'll only get the first page (100 results) for each hook to be efficient
        # This is sufficient to get a good estimate of the most popular hooks
        params = {
            "q": query,
            "per_page": 100,
            "page": 1
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                
                if remaining == 0:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(reset_time - time.time() + 1, 1)
                    
                    print(f"  Rate limit reached. Waiting for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
            
            response.raise_for_status()
            data = response.json()
            
            total_results = data.get("total_count", 0)
            print(f"  Found {total_results} code matches for {hook}")
            

            if "items" in data and data["items"]:
                for item in data["items"]:
                    repo_name = item["repository"]["full_name"]

                    if repo_name not in repositories:
                        repo_url = f"https://api.github.com/repos/{repo_name}"
                        repo_response = requests.get(repo_url, headers=headers)

                        if repo_response.status_code == 200:
                            repo_data = repo_response.json()
                            
                            # Check if repo_data is None
                            if repo_data:
                                description = repo_data.get("description", "").lower() if repo_data.get("description") else ""
                                topics = repo_data.get("topics", [])

                                is_react_native = (
                                    "react-native" in description or
                                    "react native" in description or
                                    "react-native" in topics or
                                    repo_name.lower().find("react-native") != -1
                                )

                                if is_react_native:
                                    repositories[repo_name] = {
                                        "stars": repo_data.get("stargazers_count", 0),
                                        "forks": repo_data.get("forks_count", 0)
                                    }
                            else:
                                print(f"Warning: repo_data is None for {repo_name}") #add warning log
                        # ... (your existing code) ...

        except requests.exceptions.RequestException as e:
            print(f"  Error searching for {hook}: {e}")
        
        # Calculate statistics for this hook
        repo_count = len(repositories)
        total_stars = sum(repo["stars"] for repo in repositories.values())
        total_forks = sum(repo["forks"] for repo in repositories.values())
        
        hook_stats[hook] = {
            "repository_count": repo_count,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "avg_stars_per_repo": total_stars / repo_count if repo_count > 0 else 0
        }
        
        print(f"  Found {repo_count} React Native repositories using {hook}")
        print(f"  Total stars: {total_stars:,}")
        print()
    
    # Sort hooks by total stars and get top 10
    sorted_hooks = sorted(
        hook_stats.items(),
        key=lambda x: x[1]["total_stars"],
        reverse=True
    )[:10]
    
    return sorted_hooks

def main():
    # Get GitHub API token from environment variable
    api_token = "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"
    
    if not api_token:
        print("Error: GitHub API token not found")
        print("Please set your GitHub API token as an environment variable:")
        print("  export GITHUB_API_TOKEN=your_token_here")
        print("\nYou can create a token at: https://github.com/settings/tokens")
        return
    
    print("Analyzing Popular React Native Hooks")
    print("===================================")
    
    top_hooks = search_react_native_hooks(api_token)
    
    print("\nTop 10 Most Popular React Native Hooks (by Repository Stars):")
    print("===========================================================")
    
    for i, (hook, stats) in enumerate(top_hooks, 1):
        print(f"{i}. {hook}")
        print(f"   Used in {stats['repository_count']} repositories")
        print(f"   Total stars: {stats['total_stars']:,}")
        print(f"   Average stars per repo: {stats['avg_stars_per_repo']:.1f}")
        print(f"   Total forks: {stats['total_forks']:,}")
        print()

if __name__ == "__main__":
    main()