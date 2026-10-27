# PyInstaller: dist\VibracionURSA\ (programa sin consola + dependencias). Uso: pyinstaller VibracionURSA.spec
import sys

sys.path.insert(0, SPECPATH)  # noqa: F821  (SPECPATH lo define PyInstaller)

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
)

from version import __version__

# Reason: SignPath exige nombre de producto y versión en los metadatos del .exe firmado.
_v = tuple(int(x) for x in __version__.split(".")) + (0,)
VERSION = VSVersionInfo(
    ffi=FixedFileInfo(filevers=_v, prodvers=_v),
    kids=[
        StringFileInfo([StringTable("040904B0", [
            StringStruct("CompanyName", "agustin320"),
            StringStruct("FileDescription", "URSA Rumble - WinWing URSA MINOR vibration for MSFS 2024"),
            StringStruct("FileVersion", __version__),
            StringStruct("InternalName", "VibracionURSA"),
            StringStruct("LegalCopyright", "MIT License"),
            StringStruct("OriginalFilename", "VibracionURSA.exe"),
            StringStruct("ProductName", "vibracion-ursa"),
            StringStruct("ProductVersion", __version__),
        ])]),
        VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
    ],
)

a = Analysis(
    ["bandeja.py"],
    datas=[
        ("config.json", "."),
        ("recursos/SimConnect.dll", "."),
        ("recursos/icono.ico", "."),
        ("idiomas/*.json", "idiomas"),
    ],
    hiddenimports=["pystray._win32"],
    excludes=["pygame", "numpy"],
)
pyz = PYZ(a.pure)
# Reason: carpeta (onedir) y no un solo .exe: el onefile se descomprime en %TEMP% y se ejecuta desde ahí, técnica
# que los antivirus asocian a malware. La carpeta la empaqueta el instalador (instalador.iss).
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="VibracionURSA",
    console=False,
    icon="recursos/icono.ico",
    version=VERSION,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="VibracionURSA", upx=False)
