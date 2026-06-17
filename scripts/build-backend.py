"""Build Python backend into a single executable using PyInstaller."""
import subprocess
import sys
import os
import shutil

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "..", "backend")
    backend_dir = os.path.normpath(backend_dir)
    spec_file = os.path.join(backend_dir, "youtuber-backend.spec")
    dist_dir = os.path.join(backend_dir, "dist")
    build_dir = os.path.join(backend_dir, "build")

    # Clean previous builds
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    # Install dependencies
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r",
        os.path.join(backend_dir, "requirements.txt")
    ])

    # Run PyInstaller
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        spec_file,
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--clean",
        "--noconfirm",
    ])

    # Verify output
    if sys.platform == "win32":
        exe_path = os.path.join(dist_dir, "youtuber-backend.exe")
    else:
        exe_path = os.path.join(dist_dir, "youtuber-backend")

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / 1024 / 1024
        print(f"Build successful: {exe_path} ({size_mb:.1f} MB)")
    else:
        print("Build failed: executable not found")
        sys.exit(1)

if __name__ == "__main__":
    main()
