"""Diagnóstico: largo de los reportes HID de salida de los dispositivos WinWing (solo lectura)."""
import ctypes
from ctypes import wintypes

import hid

hid_dll = ctypes.WinDLL("hid")
k32 = ctypes.WinDLL("kernel32", use_last_error=True)


class HIDP_CAPS(ctypes.Structure):
    _fields_ = [("Usage", ctypes.c_ushort), ("UsagePage", ctypes.c_ushort),
                ("InputReportByteLength", ctypes.c_ushort), ("OutputReportByteLength", ctypes.c_ushort),
                ("FeatureReportByteLength", ctypes.c_ushort), ("Reserved", ctypes.c_ushort * 17),
                ("rest", ctypes.c_ushort * 10)]


k32.CreateFileW.restype = wintypes.HANDLE
for d in hid.enumerate(0x4098):
    path = d["path"].decode()
    h = k32.CreateFileW(path, 0, 3, None, 3, 0, None)
    pp = ctypes.c_void_p()
    caps = HIDP_CAPS()
    if hid_dll.HidD_GetPreparsedData(h, ctypes.byref(pp)):
        hid_dll.HidP_GetCaps(pp, ctypes.byref(caps))
        hid_dll.HidD_FreePreparsedData(pp)
    k32.CloseHandle(h)
    print(hex(d["product_id"]), d["product_string"], "in", caps.InputReportByteLength,
          "out", caps.OutputReportByteLength, "feature", caps.FeatureReportByteLength)
