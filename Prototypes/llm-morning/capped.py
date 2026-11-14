"""Runs unittest modules, or a script, under a time cap and a memory cap, so that a runaway loop cannot take the
machine down. The process exits by itself with code 98 (time) or 99 (memory).

usage: capped.py <dir> <seconds> <megabytes> test <module> [<module> ...]
       capped.py <dir> <seconds> <megabytes> run <script.py> [args ...]
"""
import ctypes
import ctypes.wintypes
import os
import runpy
import sys
import threading
import time


class PMC(ctypes.Structure):
    _fields_ = [("cb", ctypes.wintypes.DWORD), ("PageFaultCount", ctypes.wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def megabytes():
    c = PMC()
    c.cb = ctypes.sizeof(PMC)
    k = ctypes.windll.kernel32
    k.K32GetProcessMemoryInfo.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(PMC), ctypes.wintypes.DWORD]
    k.K32GetProcessMemoryInfo(k.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return max(c.WorkingSetSize, c.PagefileUsage) / 1e6, max(c.PeakWorkingSetSize, c.PeakPagefileUsage) / 1e6


def watch(seconds, limit):
    started = time.monotonic()
    while True:
        time.sleep(0.25)
        now, _ = megabytes()
        if now > limit:
            sys.stderr.write(f"\nCAPPED: {now:.0f} MB is over the {limit} MB limit; stopping.\n")
            sys.stderr.flush()
            os._exit(99)
        if time.monotonic() - started > seconds:
            import faulthandler
            sys.stderr.write(f"\nCAPPED: over the {seconds} s limit; stopping. Where it was:\n")
            faulthandler.dump_traceback(file=sys.stderr)
            sys.stderr.flush()
            os._exit(98)


root, seconds, limit, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
sys.path.insert(0, root)
os.environ.pop("GEMINI_API_KEY", None)
threading.Thread(target=watch, args=(seconds, limit), daemon=True).start()
t0 = time.monotonic()
if mode == "test":
    import unittest
    prog = unittest.main(module=None, argv=["capped"] + sys.argv[5:], exit=False)
    ok = prog.result.wasSuccessful()
else:
    sys.argv = sys.argv[5:]
    runpy.run_path(sys.argv[0], run_name="__main__")
    ok = True
print(f"capped: {time.monotonic() - t0:.0f} s, peak {megabytes()[1]:.0f} MB")
sys.exit(0 if ok else 1)
