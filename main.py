from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import all API modules
from prometheus_api import get_storage_data
from windows_storage_api import get_windows_storage_data
from linux_cpu_api import get_linux_cpu_data
from windows_cpu_api import get_windows_cpu_data
from linux_memory_api import get_linux_memory_data
from windows_memory_api import get_windows_memory_data
from overview_api import get_overview_data

app = FastAPI()

# Mount static files for ECharts or CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# 1. Overview Page
@app.get("/", response_class=HTMLResponse)
@app.get("/overview", response_class=HTMLResponse)
async def overview_page(request: Request):
    data = get_overview_data()
    # Debug: print(data) # Uncomment to see data structure in console
    return templates.TemplateResponse("overview.html", {
        "request": request, 
        "hosts": data,
        "active_page": "overview"
    })

# 2. Linux Disk Page
@app.get("/storage", response_class=HTMLResponse)
async def linux_storage_page(request: Request):
    data = get_storage_data()
    return templates.TemplateResponse("storage.html", {
        "request": request,
        "charts_devices": data,
        "table_devices": data,
        "n_percent": 85,
        "active_page": "linux_disk"
    })

# 3. Windows Disk Page
@app.get("/windows-storage", response_class=HTMLResponse)
async def windows_storage_page(request: Request):
    data = get_windows_storage_data()
    return templates.TemplateResponse("windows_storage.html", {
        "request": request,
        "charts_devices": data,
        "table_devices": data,
        "n_percent": 85,
        "active_page": "windows_disk"
    })

# 4. Linux CPU Page
@app.get("/linux-cpu", response_class=HTMLResponse)
async def linux_cpu_page(request: Request):
    data = get_linux_cpu_data()
    return templates.TemplateResponse("cpu_monitor.html", {
        "request": request,
        "devices": data,
        "platform": "Linux",
        "active_page": "linux_cpu"
    })

# 5. Windows CPU Page
@app.get("/windows-cpu", response_class=HTMLResponse)
async def windows_cpu_page(request: Request):
    data = get_windows_cpu_data()
    return templates.TemplateResponse("cpu_monitor.html", {
        "request": request,
        "devices": data,
        "platform": "Windows",
        "active_page": "windows_cpu"
    })

# 6. Linux Memory Page
@app.get("/linux-mem", response_class=HTMLResponse)
async def linux_memory_page(request: Request):
    data = get_linux_memory_data()
    return templates.TemplateResponse("memory_monitor.html", {
        "request": request,
        "devices": data,
        "platform": "Linux",
        "active_page": "linux_mem"
    })

# 7. Windows Memory Page
@app.get("/windows-mem", response_class=HTMLResponse)
async def windows_memory_page(request: Request):
    data = get_windows_memory_data()
    return templates.TemplateResponse("memory_monitor.html", {
        "request": request,
        "devices": data,
        "platform": "Windows",
        "active_page": "windows_mem"
    })

if __name__ == "__main__":
    import uvicorn
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)