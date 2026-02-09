import requests
from requests.auth import HTTPBasicAuth

PROMETHEUS_URL = "http://127.0.0.1:9092"
USER = "admin"
PASSWORD = "password"

def get_linux_memory_data():
    # 1. Memory Usage Percentage
    usage_query = '((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes) * 100'
    # 2. Free Memory in GB
    free_query = 'node_memory_MemAvailable_bytes / (1024^3)'
    # 3. Total Memory in GB
    total_query = 'node_memory_MemTotal_bytes / (1024^3)'

    devices = []
    try:
        auth = HTTPBasicAuth(USER, PASSWORD)
        usage_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': usage_query}, auth=auth, verify=False).json()
        free_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': free_query}, auth=auth, verify=False).json()
        total_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': total_query}, auth=auth, verify=False).json()

        free_map = {item['metric'].get('instance', '').split(':')[0]: float(item['value'][1]) for item in free_res.get('data', {}).get('result', [])}
        total_map = {item['metric'].get('instance', '').split(':')[0]: float(item['value'][1]) for item in total_res.get('data', {}).get('result', [])}

        for item in usage_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', 'unknown').split(':')[0]
            usage = round(float(item['value'][1]), 2)
            total = round(total_map.get(host, 0), 2)
            free = round(free_map.get(host, 0), 2)
            devices.append({
                "hostname": host,
                "usage": usage,
                "total_gb": total,
                "used_gb": round(total - free, 2),
                "free_gb": free,
                "platform": "Linux"
            })
    except Exception as e:
        print(f"Linux Memory Error: {e}")
    return devices