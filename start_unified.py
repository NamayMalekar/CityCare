"""
CityCare Clinic — Single-URL Unified Launcher.
Runs the backend API and serves the built frontend SPA on http://localhost:8000
"""
import os
import sys
import subprocess
import uvicorn

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "citycare-backend")
    frontend_dir = os.path.join(root_dir, "citycare-frontend")
    dist_dir = os.path.join(frontend_dir, "dist")

    # Ensure backend directory is in sys.path
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # 1. Build frontend if missing
    if not os.path.exists(dist_dir):
        print("Building frontend assets...")
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        subprocess.run([npm_cmd, "run", "build"], cwd=frontend_dir, check=True)

    # 2. Seed doctor account
    print("Seeding doctor account...")
    subprocess.run([sys.executable, "seed_doctor.py"], cwd=backend_dir, check=True)

    # 3. Start server
    print("\n========================================================")
    print(" CityCare Clinic running at: http://localhost:8000")
    print(" Doctor Login:  dr.meera@citycare.clinic / doctor123")
    print("========================================================\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
