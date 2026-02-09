import requests
from requests.auth import HTTPBasicAuth

# Prometheus configuration
PROMETHEUS_URL = "http://127.0.0.1:9092" 
USER = "admin"
PASSWORD = "password"

def get_windows_storage_data():
    # Queries for windows_exporter
    # 1. Usage percentage
    usage_query = '((windows_logical_disk_size_bytes{volume=~"[A-Z]:"} - windows_logical_disk_free_bytes{volume=~"[A-Z]:"}) / windows_logical_disk_size_bytes{volume=~"[A-Z]:"}) * 100'
    # 2. Free bytes
    free_query = 'windows_logical_disk_free_bytes{volume=~"[A-Z]:"}'
    # 3. Total size bytes
    total_query = 'windows_logical_disk_size_bytes{volume=~"[A-Z]:"}'
    # 4. Volume Information (Label)
    label_query = 'windows_logical_disk_info'

    devices = []
    try:
        # Fetching data from Prometheus
        auth = HTTPBasicAuth(USER, PASSWORD)
        usage_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': usage_query}, auth=auth, verify=False, timeout=5).json()
        free_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': free_query}, auth=auth, verify=False, timeout=5).json()
        total_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': total_query}, auth=auth, verify=False, timeout=5).json()
        label_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': label_query}, auth=auth, verify=False, timeout=5).json()

        # Build lookup maps
        # Key format: "IP_DriveLetter" (e.g., "192.168.1.10_C:")
        free_map = {}
        for item in free_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            key = f"{host}_{item['metric'].get('volume')}"
            free_map[key] = float(item['value'][1])

        total_map = {}
        for item in total_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            key = f"{host}_{item['metric'].get('volume')}"
            total_map[key] = float(item['value'][1])

        label_map = {}
        for item in label_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            key = f"{host}_{item['metric'].get('volume')}"
            label_map[key] = item['metric'].get('volume_name', '')

        # Combine all data into final list
        for item in usage_res.get('data', {}).get('result', []):
            metric = item['metric']
            host = metric.get('instance', 'unknown').split(':')[0]
            drive = metric.get('volume', 'unknown')
            key = f"{host}_{drive}"
            
            usage_pct = round(float(item['value'][1]), 2)
            f_bytes = free_map.get(key, 0)
            t_bytes = total_map.get(key, 0)
            u_bytes = t_bytes - f_bytes
            
            devices.append({
                "hostname": host,
                "platform": "Windows",
                "mountpoint": drive,  # Using mountpoint to align with HTML template
                "label": label_map.get(key, "No Label"),
                "usage": usage_pct,
                "used_gb": round(u_bytes / (1024**3), 2),
                "free_gb": round(f_bytes / (1024**3), 2),
                "total_gb": round(t_bytes / (1024**3), 2)
            })
    except Exception as e:
        print(f"Error fetching Windows storage data: {e}")
    
    return devices