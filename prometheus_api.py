import requests
from requests.auth import HTTPBasicAuth

# Prometheus configuration
PROMETHEUS_URL = "http://127.0.0.1:9092" 
USER = "admin"
PASSWORD = "password"

def get_storage_data():
    # 1. Query for usage percentage
    usage_query = '(1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|squashfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|squashfs"})) * 100'
    # 2. Query for available bytes
    free_query = 'node_filesystem_avail_bytes{fstype!~"tmpfs|squashfs"}'
    # 3. Query for total size bytes
    total_query = 'node_filesystem_size_bytes{fstype!~"tmpfs|squashfs"}'

    devices = []
    try:
        # Fetch data from Prometheus API
        usage_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': usage_query}, 
                                 auth=HTTPBasicAuth(USER, PASSWORD), verify=False, timeout=5).json()
        free_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': free_query}, 
                                auth=HTTPBasicAuth(USER, PASSWORD), verify=False, timeout=5).json()
        total_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': total_query}, 
                                 auth=HTTPBasicAuth(USER, PASSWORD), verify=False, timeout=5).json()

        # Create mapping for free space and total space
        free_map = {}
        for item in free_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            key = f"{host}_{item['metric'].get('mountpoint')}"
            free_map[key] = float(item['value'][1])

        total_map = {}
        for item in total_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            key = f"{host}_{item['metric'].get('mountpoint')}"
            total_map[key] = float(item['value'][1])

        # Combine all data
        for item in usage_res.get('data', {}).get('result', []):
            metric = item['metric']
            raw_instance = metric.get('instance', 'unknown')
            clean_host = raw_instance.split(':')[0] # Remove port number
            
            mount = metric.get('mountpoint', 'unknown')
            usage_pct = round(float(item['value'][1]), 2)
            
            key = f"{clean_host}_{mount}"
            
            # Perform calculations and unit conversion (Bytes to GB)
            f_bytes = free_map.get(key, 0)
            t_bytes = total_map.get(key, 0)
            u_bytes = t_bytes - f_bytes
            
            devices.append({
                "hostname": clean_host,
                "platform": "Linux",
                "mountpoint": mount,
                "usage": usage_pct,
                "used_gb": round(u_bytes / (1024**3), 2),
                "free_gb": round(f_bytes / (1024**3), 2),
                "total_gb": round(t_bytes / (1024**3), 2)
            })
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return devices