"""Build Python backend into a single executable using PyInstaller."""
import subprocess
import sys
import os
import shutil

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.normpath(os.path.join(script_dir, "..", "backend"))
    spec_file = os.path.join(backend_dir, "youtuber-backend.spec")
    dist_dir = os.path.join(backend_dir, "dist")
    build_dir = os.path.join(backend_dir, "build")

    print(f"Script dir: {script_dir}")
    print(f"Backend dir: {backend_dir}")
    print(f"Spec file: {spec_file} (exists: {os.path.exists(spec_file)})")

    # Clean previous builds
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Install dependencies
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r",
        os.path.join(backend_dir, "requirements.txt")
    ])

    # Run PyInstaller from backend dir so relative paths in spec resolve correctly
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        spec_file,
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--clean",
        "--noconfirm",
    ], cwd=backend_dir)

    # List dist directory contents for debugging
    if os.path.exists(dist_dir):
        print(f"Dist contents: {os.listdir(dist_dir)}")
    else:
        print(f"Dist dir does not exist: {dist_dir}")

    # Verify output
    if sys.platform == "win32":
        exe_path = os.path.join(dist_dir, "youtuber-backend.exe")
    else:
        exe_path = os.path.join(dist_dir, "youtuber-backend")

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / 1024 / 1024
        print(f"Build successful: {exe_path} ({size_mb:.1f} MB)")
    else:
        print(f"Build failed: {exe_path} not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
