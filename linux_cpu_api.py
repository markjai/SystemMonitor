import requests
from requests.auth import HTTPBasicAuth

PROMETHEUS_URL = "http://127.0.0.1:9092"
USER = "admin"
PASSWORD = "password"

def get_linux_cpu_data():
    # 1. Average CPU Usage (1 - idle)
    usage_query = '(1 - avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100'
    # 2. CPU Core Count
    cores_query = 'count by(instance) (node_cpu_seconds_total{mode="idle"})'

    devices = []
    try:
        auth = HTTPBasicAuth(USER, PASSWORD)
        usage_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': usage_query}, auth=auth, verify=False).json()
        cores_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': cores_query}, auth=auth, verify=False).json()

        cores_map = {item['metric'].get('instance', '').split(':')[0]: item['value'][1] for item in cores_res.get('data', {}).get('result', [])}

        for item in usage_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', 'unknown').split(':')[0]
            usage = round(float(item['value'][1]), 2)
            devices.append({
                "hostname": host,
                "usage": usage,
                "cores": cores_map.get(host, "N/A"),
                "platform": "Linux"
            })
    except Exception as e:
        print(f"Linux CPU Error: {e}")
    return devices