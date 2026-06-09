# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pacman/main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('pacman/assets', 'pacman/assets'), ('pacman/highscores.json', 'pacman'), ('pacman/game/saves/save.txt', 'pacman/game/saves')],
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
    [],
    exclude_binaries=True,
    name='pacman',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pacman',
)
