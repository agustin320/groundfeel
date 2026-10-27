# PyInstaller: un solo .exe sin consola. Uso: pyinstaller VibracionURSA.spec
a = Analysis(
    ["bandeja.py"],
    datas=[
        ("config.json", "."),
        ("recursos/SimConnect.dll", "."),
        ("recursos/icono.ico", "."),
    ],
    hiddenimports=["pystray._win32"],
    excludes=["pygame", "numpy"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="VibracionURSA",
    console=False,
    icon="recursos/icono.ico",
    upx=False,
)
