import requests
from requests.auth import HTTPBasicAuth

# Prometheus configuration
PROMETHEUS_URL = "http://127.0.0.1:9092"
USER = "admin"
PASSWORD = "password"

def get_windows_memory_data():
    # Use the metrics you found in your Prometheus UI
    # 1. Query for free memory
    free_query = 'windows_memory_physical_free_bytes'
    # 2. Query for total memory (Usually follows the same naming convention)
    # If this returns 0, please check if it should be 'windows_cs_physical_memory_bytes'
    total_query = 'windows_memory_physical_total_bytes'

    devices = []
    try:
        auth = HTTPBasicAuth(USER, PASSWORD)
        
        # Fetch data from Prometheus
        total_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': total_query}, auth=auth, verify=False, timeout=5).json()
        free_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': free_query}, auth=auth, verify=False, timeout=5).json()

        # Build mapping for free memory: { "IP": value }
        free_map = {}
        for item in free_res.get('data', {}).get('result', []):
            host = item['metric'].get('instance', '').split(':')[0]
            free_map[host] = float(item['value'][1])

        # Use total_res as the primary loop to build the device list
        results = total_res.get('data', {}).get('result', [])
        
        # If total_query failed to find metrics, try the alternative common name
        if not results:
            alt_total_query = 'windows_cs_physical_memory_bytes'
            total_res = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': alt_total_query}, auth=auth, verify=False, timeout=5).json()
            results = total_res.get('data', {}).get('result', [])

        for item in results:
            host = item['metric'].get('instance', 'unknown').split(':')[0]
            t_bytes = float(item['value'][1])
            f_bytes = free_map.get(host, 0)
            u_bytes = t_bytes - f_bytes
            
            # Calculate usage percentage in Python to ensure reliability
            usage_pct = 0
            if t_bytes > 0:
                usage_pct = round((u_bytes / t_bytes) * 100, 2)
            
            # Align keys with memory_monitor.html
            devices.append({
                "hostname": host,
                "usage": usage_pct,
                "total_gb": round(t_bytes / (1024**3), 2),
                "used_gb": round(u_bytes / (1024**3), 2),
                "free_gb": round(f_bytes / (1024**3), 2),
                "platform": "Windows"
            })
            
    except Exception as e:
        # Log error with English comments as requested
        print(f"Windows Memory API Error: {str(e)}")
    
    return devices