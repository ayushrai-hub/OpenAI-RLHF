# ideal_completion.py
import time
import json
import requests
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from colorama import init, Fore, Style

# Initialize Colorama
init()

def fetch_bearer_token(page_url):
    """Use Selenium to get the bearer token from the specified URL."""
    chrome_opts = Options()
    chrome_opts.add_argument('--ignore-certificate-errors')
    chrome_opts.add_argument('--incognito')
    chrome_opts.add_argument('--headless')
    service = ChromeService(executable_path='chromedriver.exe')  # Adjust the path if needed

    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.get(page_url)

    try:
        # Briefly pause to let the page load
        time.sleep(3)

        # Run JavaScript to access all localStorage items
        keys = driver.execute_script("return Object.keys(localStorage);")
        
        token_key = next((key for key in keys if key.startswith('token_')), None)

        if token_key:
            stored_data = driver.execute_script(f"return localStorage.getItem('{token_key}');")
            if stored_data:
                data = json.loads(stored_data)
                token_value = data.get('value', 'Token not found')
                driver.quit()
                return token_value
            else:
                driver.quit()
                return 'Token not found'
        else:
            driver.quit()
            return 'Token key not found'
    except Exception:
        driver.quit()
        return 'Token key not found'

def send_request(headers, url, payload):
    """Make a POST request to the specified URL with the given headers and payload."""
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}

def print_output(action, result):
    """Format and display the output nicely."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] Action: {Fore.CYAN}{action.capitalize()}{Style.RESET_ALL}")
    
    if 'detail' in result:
        detail = result['detail']
        required_invites = detail.get('need_invites', 'N/A')
        block_duration = detail.get('blocked_until', 'N/A')
        if block_duration != 'N/A':
            current_time = time.time()
            remaining_sleep = block_duration - current_time
            if remaining_sleep > 0:
                print(f"[{now}] Required invites: {Fore.YELLOW}{required_invites}{Style.RESET_ALL}")
                print(f"[{now}] Blocked until: {Fore.YELLOW}{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block_duration))}{Style.RESET_ALL}")
                return remaining_sleep
            else:
                print(f"[{now}] Required invites: {Fore.GREEN}{required_invites}{Style.RESET_ALL}")
                print(f"[{now}] Blocked until: {Fore.GREEN}{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block_duration))}{Style.RESET_ALL}")
                print(f"[{now}] {Fore.GREEN}Request completed.{Style.RESET_ALL}")
                return 0
        else:
            print(f"[{now}] Required invites: {Fore.RED}{required_invites}{Style.RESET_ALL}")
            print(f"[{now}] {Fore.RED}No blocking info available.{Style.RESET_ALL}")
            return 0
    else:
        print(f"[{now}] Successfully claimed {Fore.GREEN}{action.capitalize()}.{Style.RESET_ALL}")
        return 0

def handle_accounts(filepath):
    block_until_time = 0
    end_farming_time = datetime.now() + timedelta(hours=3)  # Adjust as required

    while True:
        try:
            with open(filepath, 'r') as file:
                accounts = file.readlines()

            for idx, account_line in enumerate(accounts, start=1):
                page_url = f"https://example.site/#tgWebAppData={account_line.strip()}"
                raw_account_data = urllib.parse.unquote(account_line)
                query_components = urllib.parse.parse_qs(raw_account_data)
                encoded_user_data = query_components.get('user', [None])[0]

                if not encoded_user_data:
                    print(f"{Fore.RED}Invalid account data. Skipping to next account.{Style.RESET_ALL}")
                    continue

                decoded_user_data = urllib.parse.unquote(encoded_user_data)

                user_data = json.loads(decoded_user_data)

                # Get the "first_name" and "id"
                first_name_of_user = user_data.get('first_name', 'Unknown')
                user_account_id = user_data.get('id', 'Unknown')

                token = fetch_bearer_token(page_url)
                if token in ['Token not found', 'Token key not found']:
                    print(f"{Fore.RED}Could not fetch token. Moving to next account.{Style.RESET_ALL}")
                    continue

                headers = {
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-US,en;q=0.9',
                    'authorization': f'Bearer {token}',
                    'referer': 'https://example.site/',
                    'user-agent': 'Mozilla/5.0'
                }
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Account number : {Fore.GREEN}{idx}/{len(accounts)}{Style.RESET_ALL}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Name : {Fore.GREEN}{first_name_of_user}{Style.RESET_ALL}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] User ID : {Fore.GREEN}{user_account_id}{Style.RESET_ALL}\n")

                endpoints_dict = {
                    'sendTokens': 'https://example.site/api/bonuses/tokens/',
                    'randomDraw': 'https://example.site/api/random_draw/',
                    'slideToken': 'https://example.site/api/slide_token/'
                }

                payload_map = {
                    'sendTokens': {'tokens': 915},
                    'randomDraw': {},
                    'slideToken': {'tokens': 3000}
                }

                for action, endpoint_url in endpoints_dict.items():
                    response = send_request(headers, endpoint_url, payload_map[action])
                    duration_to_sleep = print_output(action, response)

                    if duration_to_sleep > 0:
                        block_until_time = max(block_until_time, time.time() + duration_to_sleep)
                        break
                    else:
                        block_until_time = 0

                if block_until_time > time.time():
                    break

            if block_until_time > time.time():
                pause_time = block_until_time - time.time()
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {Fore.MAGENTA}Waiting for {pause_time:.2f} seconds before retrying...{Style.RESET_ALL}")
                time.sleep(max(pause_time, 1))

            if datetime.now() >= end_farming_time:
                print(f"{Fore.GREEN}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Farming ended at : {end_farming_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                break
            break

        except FileNotFoundError:
            print(f"{Fore.RED}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: The file '{filepath}' was not found.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] An error happened: {e}{Style.RESET_ALL}")
            continue
        

if __name__ == "__main__":
    handle_accounts('account_data.txt')