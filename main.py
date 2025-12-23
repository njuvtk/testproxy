import requests
import concurrent.futures
import threading
import os

# --- 配置 ---
SOURCES = {
    "http": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "socks4": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "socks5": "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt"
}
OUTPUT_DIR = "results"  # 结果保存的文件夹
MAX_THREADS = 50
TIMEOUT = 5
TEST_URL = "http://httpbin.org/ip"
# -----------

def download_list(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return [line.strip() for line in resp.text.splitlines() if line.strip()]
    except:
        pass
    return []

def check_proxy(proxy_str, protocol):
    if "://" not in proxy_str:
        full_url = f"{protocol}://{proxy_str}"
    else:
        full_url = proxy_str
    
    proxies = {"http": full_url, "https": full_url}
    try:
        resp = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        if resp.status_code == 200:
            return full_url
    except:
        return None

def process_category(category, url):
    proxies = download_list(url)
    if not proxies:
        return

    valid_proxies = []
    print(f"Checking {category} ({len(proxies)})...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_proxy = {executor.submit(check_proxy, p, category): p for p in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            if result := future.result():
                valid_proxies.append(result)

    # 保存结果
    file_path = os.path.join(OUTPUT_DIR, f"valid_{category}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(valid_proxies))
    
    print(f"Saved {len(valid_proxies)} {category} proxies.")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for category, url in SOURCES.items():
        process_category(category, url)

if __name__ == "__main__":
    main()
