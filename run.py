import os
import sys
import time
import subprocess
import socket
import webbrowser


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def kill_process_on_port(port: int):
    try:
        if sys.platform == "win32":
            cmd = f'powershell -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"'
            subprocess.run(cmd, shell=True, capture_output=True)
    except Exception:
        pass


def main():
    print("=" * 65)
    print("  TRACE — AI Reunification & Claim Verification Engine")
    print("  Team Grey Matter (Niviya Albert, Adithyan M J, Diya Paramanand)")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 1. Clean up lingering processes on port 8000 and 8501
    for p in [8000, 8501]:
        if is_port_in_use(p):
            print(f"[!] Port {p} was in use. Freeing port...")
            kill_process_on_port(p)
            time.sleep(1)

    # 2. Initialize DB, seed data & warm up models
    print("\n[1/3] Initializing SQLite database, seed assets & offline AI cache...")
    from backend.seed import init_db
    from backend.embeddings import warmup_embeddings
    init_db()
    warmup_embeddings()

    # 3. Start FastAPI Backend
    print("\n[2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "warning",
    ]
    backend_proc = subprocess.Popen(backend_cmd)

    # Wait for backend to be ready
    for _ in range(10):
        if is_port_in_use(8000):
            break
        time.sleep(0.5)

    # 4. Start Streamlit Frontend
    print("\n[3/3] Starting Streamlit Staff Dashboard on http://localhost:8501 ...")
    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port",
        "8501",
        "--server.headless",
        "false",
        "--theme.base",
        "dark",
    ]
    streamlit_proc = subprocess.Popen(streamlit_cmd)

    print("\n" + "=" * 65)
    print("  ✅ TRACE System is up and running!")
    print("  👉 Open Staff Dashboard: http://localhost:8501")
    print("  👉 Backend API Docs:     http://127.0.0.1:8000/docs")
    print("  Press Ctrl+C in this terminal to shut down.")
    print("=" * 65 + "\n")

    try:
        # Auto open browser
        time.sleep(1.5)
        webbrowser.open("http://localhost:8501")
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down TRACE services...")
        streamlit_proc.terminate()
        backend_proc.terminate()


if __name__ == "__main__":
    main()
