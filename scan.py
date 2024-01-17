import socket
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_network

def check_ip(ip, port):
    try:
        socket.create_connection((ip, port), timeout=1)
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def get_title(ip, port):
    try:
        response = requests.get(f"http://{ip}:{port}", timeout=1)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip()
        return title
    except (requests.RequestException, AttributeError):
        return None

def check_web(ip):
    try:
        response = requests.get(f"http://{ip}", timeout=1)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        pass
    return False

def save_to_file(ip, title, filename):
    with open(filename, 'a') as file:
        file.write(f"{ip}  {title}\n")

def scan_ip(ip, progress_bar, filename):
    result = None
    if check_ip(ip, 80) or check_ip(ip, 443):
        if check_web(ip):
            title = get_title(ip, 80) or get_title(ip, 443)
            save_to_file(ip, title, filename)
            result = f"IP: {ip}  Title: {title}"
    progress_bar.update(1)
    return result

def scan_ip_range(ip_range, filename, progress_bar):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda ip: scan_ip(str(ip), progress_bar, filename), ip_range))

    for result in results:
        if result:
            print(result)

def main():
    input_str = input("請輸入欲掃描的IP範圍（以逗號分隔）: ")
    ip_ranges_str = input_str.split(',')

    with open('./scan.txt', 'w') as file:
        file.write('')

    for ip_range_str in ip_ranges_str:
        ip_range = ip_network(ip_range_str, strict=False)
        subnets = list(ip_range.subnets())
        progress_bar = tqdm(total=len(list(ip_range)), desc=f"正在掃描 {ip_range.network_address}/24", position=0)
        for subnet in subnets:
            scan_ip_range(subnet, './scan.txt', progress_bar)
        progress_bar.close()

if __name__ == "__main__":
    main()

