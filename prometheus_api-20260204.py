import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROMETHEUS_URL = "https://localhost:9092"
USER = "admin"
PASSWORD = "sinopacadmin"

def get_storage_data():
    # Unified PromQL for both Linux and Windows metrics
    query = """
    label_replace(
        (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|squashfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|squashfs"})) * 100,
        "platform", "Linux", "", ""
    ) 
    or 
    label_replace(
        (1 - (windows_logical_disk_free_bytes / windows_logical_disk_size_bytes)) * 100,
        "platform", "Windows", "", ""
    )
    """
    try:
        # Request data with Basic Auth and ignore SSL verify
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={'query': query},
            auth=HTTPBasicAuth(USER, PASSWORD),
            verify=False 
        )
        response.raise_for_status()
        results = response.json()['data']['result']
        
        devices = []
        for r in results:
            m = r['metric']
            # Identify mount point or drive letter based on platform
            devices.append({
                "hostname": m.get('instance', 'N/A'),
                "platform": m.get('platform'),
                "mountpoint": m.get('mountpoint') or m.get('device'),
                "usage": round(float(r['value'][1]), 2)
            })
        return devices
    except Exception as e:
        print(f"Error fetching data from Prometheus: {e}")
        return []