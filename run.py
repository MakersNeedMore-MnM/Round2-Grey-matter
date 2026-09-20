import os
import sys
import time
import subprocess
import webbrowser


def main():
    print("=" * 65)
    print("  TRACE — AI Reunification & Claim Verification Engine")
    print("  Team Grey Matter (Niviya Albert, Adithyan M J, Diya Paramanand)")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 1. Initialize DB and seed data
    print("\n[1/3] Initializing SQLite database and seed assets...")
    from backend.seed import init_db
    init_db()

    # 2. Start FastAPI Backend
    print("\n[2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    backend_proc = subprocess.Popen(backend_cmd)

    time.sleep(2)

    # 3. Start Streamlit Frontend
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
    print("  TRACE System is running!")
    print("  - Backend API: http://127.0.0.1:8000/docs")
    print("  - Staff UI:    http://localhost:8501")
    print("  Press Ctrl+C to shut down.")
    print("=" * 65 + "\n")

    try:
        streamlit_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down TRACE services...")
        streamlit_proc.terminate()
        backend_proc.terminate()


if __name__ == "__main__":
    main()
