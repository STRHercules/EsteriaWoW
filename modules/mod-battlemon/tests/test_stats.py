"""Compile and run tests/test_stats.cpp with whatever C++ compiler is available."""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tests', 'test_stats.cpp')
out = os.path.join(tempfile.mkdtemp(), 'test_stats.exe')

cxx = shutil.which('g++') or shutil.which('clang++')
if cxx:
    cmd = [cxx, '-std=c++17', '-Wall', '-I', os.path.join(ROOT, 'src'), SRC, '-o', out]
else:
    # MSVC: load the developer environment from vcvars64.bat, then call cl.
    vcvars = sorted(glob.glob(r'C:\Program Files*\Microsoft Visual Studio\*\*\VC\Auxiliary\Build\vcvars64.bat'))
    if not vcvars:
        sys.exit('no C++ compiler found (g++, clang++ or MSVC)')
    cmd = ('call "%s" >nul && cl /nologo /EHsc /std:c++17 /W4 /I "%s" "%s" /Fe:"%s" /Fo:"%s/"'
           % (vcvars[-1], os.path.join(ROOT, 'src'), SRC, out, os.path.dirname(out).replace(os.sep, '/')))
subprocess.run(cmd, shell=not cxx, check=True, stdout=subprocess.DEVNULL if not cxx else None)
subprocess.run([out], check=True)
