# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['simple_stock_predictor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['matplotlib.backends.backend_tkagg', 'numpy', 'requests', 'tkinter', 'pandas', 'akshare', 'datetime', 'threading', 'json', 'ssl', 'urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'transformers', 'plotly', 'qlib', 'jupyter', 'IPython', 'pytest', 'scipy', 'sklearn', 'huggingface_hub'],
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
    name='QuantPredictProEnhanced',
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
)
