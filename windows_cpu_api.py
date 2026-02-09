import requests
from requests.auth import HTTPBasicAuth  # 修正重點：必須匯入此行

# Prometheus configuration
PROMETHEUS_URL = "http://127.0.0.1:9092"
USER = "admin"
PASSWORD = "password"

def get_windows_cpu_data():
    # 1. Windows CPU Usage (Percentage)
    usage_query = '100 - (avg by (instance) (rate(windows_cpu_time_total{mode="idle"}[5m])) * 100)'
    # 2. Windows CPU Core Count
    cores_query = 'count by(instance) (windows_cpu_time_total{mode="idle"})'

    devices = []
    try:
        auth = HTTPBasicAuth(USER, PASSWORD)
        usage_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': usage_query}, auth=auth, verify=False, timeout=5).json()
        cores_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': cores_query}, auth=auth, verify=False, timeout=5).json()

        # Build cores map { "IP": "CoreCount" }
        cores_map = {}
        for item in cores_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            cores_map[host] = item['value'][1]

        # Combine data
        for item in usage_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', 'unknown').split(':')[0]
            usage = round(float(item['value'][1]), 2)
            
            devices.append({
                "hostname": host,
                "usage": usage,
                "cores": cores_map.get(host, "N/A"),
                "platform": "Windows"
            })
    except Exception as e:
        print(f"Windows CPU Error: {e}")
    
    return devices