from prometheus_api import get_storage_data
from windows_storage_api import get_windows_storage_data
from linux_cpu_api import get_linux_cpu_data
from windows_cpu_api import get_windows_cpu_data
from linux_memory_api import get_linux_memory_data
from windows_memory_api import get_windows_memory_data

def get_status_color(value, red_thresh, yellow_thresh):
    try:
        val = float(value)
        if val >= red_thresh: return "red"
        if val >= yellow_thresh: return "yellow"
        return "green"
    except:
        return "green"

def get_overview_data():
    # Fetch all data and ensure they are lists
    l_disk = get_storage_data() or []
    w_disk = get_windows_storage_data() or []
    l_cpu = get_linux_cpu_data() or []
    w_cpu = get_windows_cpu_data() or []
    l_mem = get_linux_memory_data() or []
    w_mem = get_windows_memory_data() or []

    hosts_map = {}

    def init_host(name, os_type):
        if name not in hosts_map:
            hosts_map[name] = {
                "hostname": str(name),
                "os": os_type,
                "cpu": {"usage": 0, "status": "green"},
                "mem": {"usage": 0, "status": "green"},
                "disk": []
            }

    # 1. Process CPU
    for c in l_cpu:
        name = c.get('hostname')
        if not name: continue
        init_host(name, "Linux")
        usage = c.get('usage', 0)
        hosts_map[name]['cpu'] = {"usage": usage, "status": get_status_color(usage, 95, 80)}

    for c in w_cpu:
        name = c.get('hostname')
        if not name: continue
        init_host(name, "Windows")
        usage = c.get('usage', 0)
        hosts_map[name]['cpu'] = {"usage": usage, "status": get_status_color(usage, 95, 80)}

    # 2. Process Memory
    for m in l_mem:
        name = m.get('hostname')
        if not name: continue
        init_host(name, "Linux")
        usage = m.get('usage', 0)
        hosts_map[name]['mem'] = {"usage": usage, "status": get_status_color(usage, 85, 70)}

    for m in w_mem:
        name = m.get('hostname')
        if not name: continue
        init_host(name, "Windows")
        usage = m.get('usage', 0)
        hosts_map[name]['mem'] = {"usage": usage, "status": get_status_color(usage, 85, 70)}

    # 3. Process Disk
    for d in l_disk:
        name = d.get('hostname')
        if not name: continue
        init_host(name, "Linux")
        usage = d.get('usage', 0)
        hosts_map[name]['disk'].append({
            "label": d.get('mountpoint', '/'),
            "usage": usage, 
            "status": get_status_color(usage, 85, 70)
        })

    for d in w_disk:
        name = d.get('hostname')
        if not name: continue
        init_host(name, "Windows")
        usage = d.get('usage', 0)
        hosts_map[name]['disk'].append({
            "label": d.get('mountpoint', 'C:'),
            "usage": usage,
            "status": get_status_color(usage, 85, 70)
        })

    return list(hosts_map.values())