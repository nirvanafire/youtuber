# CI/CD Packaging & Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up GitHub Actions workflows to automatically build Windows (.exe/.msi) and macOS (.dmg) installers, with Python backend bundled via PyInstaller and frontend via electron-builder.

**Architecture:** Two-stage pipeline: Stage 1 builds Python backend into single executable via PyInstaller. Stage 2 builds Electron frontend with electron-builder, embedding the Python executable as extraResources. Triggered on git tag push.

**Tech Stack:** GitHub Actions, PyInstaller, electron-builder, Node.js 20, Python 3.12

---

## File Structure

```
.github/
└── workflows/
    ├── build-windows.yml
    ├── build-macos.yml
    └── release.yml
backend/
└── youtuber-backend.spec          # PyInstaller spec file
electron/
└── src/renderer/electron-builder.yml  # electron-builder config
scripts/
└── build-backend.py               # Build script for PyInstaller
```

---

## Task 1: PyInstaller Spec File + Build Script

**Files:**
- Create: `backend/youtuber-backend.spec`
- Create: `scripts/build-backend.py`

- [ ] **Step 1: Create PyInstaller spec file**

```python
# backend/youtuber-backend.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = collect_submodules('yt_dlp')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports + [
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='youtuber-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

- [ ] **Step 2: Create build script**

```python
# scripts/build-backend.py
"""Build Python backend into a single executable using PyInstaller."""
import subprocess
import sys
import os
import shutil

def main():
    backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
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
```

- [ ] **Step 3: Test PyInstaller build locally**

Run: `cd backend && python -m PyInstaller youtuber-backend.spec --clean --noconfirm`
Expected: `dist/youtuber-backend.exe` (or `youtuber-backend` on macOS/Linux) created

- [ ] **Step 4: Test the built executable**

Run: `./backend/dist/youtuber-backend`
Expected: `PORT=xxxxx` output, server starts

- [ ] **Step 5: Commit**

```bash
git add backend/youtuber-backend.spec scripts/build-backend.py
git commit -m "build: add PyInstaller spec and build script for backend packaging"
```

---

## Task 2: electron-builder Configuration

**Files:**
- Create: `electron/src/renderer/electron-builder.yml`
- Modify: `electron/package.json`

- [ ] **Step 1: Create electron-builder config**

```yaml
# electron/src/renderer/electron-builder.yml
appId: com.youtuber.app
productName: Youtuber
directories:
  output: release
  buildResources: build
files:
  - dist/**/*
  - "!node_modules/**/*"
extraResources:
  - from: "../../backend/dist/youtuber-backend"
    to: "backend/youtuber-backend"
  - from: "../../backend/src/main.py"
    to: "backend/main.py"
  - from: "../../backend/src/"
    to: "backend/src/"
win:
  target:
    - target: nsis
      arch: [x64]
    - target: msi
      arch: [x64]
  icon: build/icon.ico
mac:
  target:
    - target: dmg
      arch: [x64, arm64]
  icon: build/icon.icns
  category: public.app-category.utilities
nsis:
  oneClick: false
  perMachine: false
  allowToChangeInstallationDirectory: true
  installerIcon: build/icon.ico
  uninstallerIcon: build/icon.ico
  installerHeaderIcon: build/icon.ico
  createDesktopShortcut: true
  createStartMenuShortcut: true
  shortcutName: Youtuber
```

- [ ] **Step 2: Update root package.json with build scripts**

```json
{
  "scripts": {
    "build:backend": "python scripts/build-backend.py",
    "build:renderer": "cd src/renderer && npm run build",
    "build:main": "tsc -p tsconfig.json",
    "build:app": "npm run build:backend && npm run build:renderer && npm run build:main && cd src/renderer && npx electron-builder --config electron-builder.yml",
    "build:win": "npm run build:app -- --win",
    "build:mac": "npm run build:app -- --mac"
  }
}
```

- [ ] **Step 3: Create placeholder icon files**

Create `electron/src/renderer/build/icon.ico` (Windows) and `electron/src/renderer/build/icon.icns` (macOS) — can use placeholder images.

- [ ] **Step 4: Commit**

```bash
git add electron/
git commit -m "build: add electron-builder config for Windows and macOS packaging"
```

---

## Task 3: GitHub Actions — Windows Build Workflow

**Files:**
- Create: `.github/workflows/build-windows.yml`

- [ ] **Step 1: Create Windows build workflow**

```yaml
# .github/workflows/build-windows.yml
name: Build Windows

on:
  push:
    tags:
      - "v*"
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build Python backend
        run: python scripts/build-backend.py

      - name: Install frontend dependencies
        run: |
          cd electron
          npm install
          cd src/renderer
          npm install

      - name: Build frontend
        run: |
          cd electron/src/renderer
          npm run build
          cd ..
          npx tsc -p tsconfig.json

      - name: Build Electron app
        run: |
          cd electron/src/renderer
          npx electron-builder --win --config electron-builder.yml
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: windows-build
          path: |
            electron/src/renderer/release/*.exe
            electron/src/renderer/release/*.msi
          retention-days: 7
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/build-windows.yml
git commit -m "ci: add GitHub Actions workflow for Windows build"
```

---

## Task 4: GitHub Actions — macOS Build Workflow

**Files:**
- Create: `.github/workflows/build-macos.yml`

- [ ] **Step 1: Create macOS build workflow**

```yaml
# .github/workflows/build-macos.yml
name: Build macOS

on:
  push:
    tags:
      - "v*"
  workflow_dispatch:

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build Python backend
        run: python scripts/build-backend.py

      - name: Install frontend dependencies
        run: |
          cd electron
          npm install
          cd src/renderer
          npm install

      - name: Build frontend
        run: |
          cd electron/src/renderer
          npm run build
          cd ..
          npx tsc -p tsconfig.json

      - name: Build Electron app
        run: |
          cd electron/src/renderer
          npx electron-builder --mac --config electron-builder.yml
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: macos-build
          path: |
            electron/src/renderer/release/*.dmg
          retention-days: 7
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/build-macos.yml
git commit -m "ci: add GitHub Actions workflow for macOS build"
```

---

## Task 5: GitHub Actions — Release Workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create release workflow that triggers on tag and creates GitHub Release**

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Build backend
        run: |
          cd backend
          pip install -r requirements.txt pyinstaller
          python ../scripts/build-backend.py
      - name: Build frontend
        run: |
          cd electron
          npm install
          cd src/renderer
          npm install
          npm run build
          cd ..
          npx tsc -p tsconfig.json
      - name: Package
        run: |
          cd electron/src/renderer
          npx electron-builder --win --config electron-builder.yml
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: windows
          path: electron/src/renderer/release/*.{exe,msi}

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Build backend
        run: |
          cd backend
          pip install -r requirements.txt pyinstaller
          python ../scripts/build-backend.py
      - name: Build frontend
        run: |
          cd electron
          npm install
          cd src/renderer
          npm install
          npm run build
          cd ..
          npx tsc -p tsconfig.json
      - name: Package
        run: |
          cd electron/src/renderer
          npx electron-builder --mac --config electron-builder.yml
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: macos
          path: electron/src/renderer/release/*.dmg

  release:
    needs: [build-windows, build-macos]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: artifacts
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            artifacts/windows/*
            artifacts/macos/*
          generate_release_notes: true
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow — build all platforms and create GitHub Release on tag"
```

---

## Task 6: CI/CD Verification

**Files:**
- No file changes

- [ ] **Step 1: Create a test tag and push to trigger workflows**

```bash
git tag v0.1.0-test
git push origin v0.1.0-test
```

- [ ] **Step 2: Monitor GitHub Actions runs**

Check that Windows and macOS builds succeed in the Actions tab.

- [ ] **Step 3: Download and test the built artifacts**

Download the .exe and .dmg from the Release page and verify they launch correctly.

- [ ] **Step 4: Delete test tag and release**

```bash
git tag -d v0.1.0-test
git push origin --delete v0.1.0-test
```

- [ ] **Step 5: Commit any workflow fixes**

```bash
git add .github/
git commit -m "fix: address CI/CD issues found during test release"
```
