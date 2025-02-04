# -*- mode: python ; coding: utf-8 -*-
import sys
import os
sys.path.insert(0, ".")
VERSION_WITH_BUILD__UNDERSCORED = os.getenv('NEW_VERSION_WITH_BUILD__UNDERSCORED')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f"KL3C__{VERSION_WITH_BUILD__UNDERSCORED}.exe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon\\icon.ico'],
    version='version.py',  # Dołączamy plik zasobów
)