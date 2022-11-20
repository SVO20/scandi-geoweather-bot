import sys
import os
import subprocess
import traceback
from time import sleep

# Path to Inkscape.exe installed in Windows
INKSCAPE_EXE_PATH = r"C:\Program Files\Inkscape\inkscape.exe"

# SVG from Wikipedia for the warming-up round versus cairosvg
SVG_SAMPLE = b"""<?xml version="1.0"?>              
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
      "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    
    <svg xmlns="http://www.w3.org/2000/svg"
     width="467" height="462">
      <rect x="80" y="60" width="250" height="250" rx="20"
          style="fill:#ff0000; stroke:#000000;stroke-width:2px;" />
      
      <rect x="140" y="120" width="250" height="250" rx="40"
          style="fill:#0000ff; stroke:#000000; stroke-width:2px;
          fill-opacity:0.7;" />
    </svg>"""


def _svg2png_inkscape(bytes_svg: bytes,
                      path_to_inkscape_exe=INKSCAPE_EXE_PATH):
    """ Harsh workaround of cairosvg.svg2png on Windows through Inkscape command-line feature
    """
    inkscape_exe = os.path.abspath(path_to_inkscape_exe)
    if not os.path.isfile(inkscape_exe):
        return None

    svg_path = os.path.join(os.path.abspath('.'), "temp.svg")
    png_path = os.path.join(os.path.abspath('.'), "temp.png")
    if os.path.exists(png_path):
        os.remove(png_path)

    with open(svg_path, "wb") as file:
        file.write(bytes_svg)
    subprocess.Popen([inkscape_exe, "-f", svg_path, "-e", png_path])

    #  wait 10 seconds for file creation by discrete intervals of 0.1 sec
    for _ in range(10 * 10):
        sleep(0.1)
        if os.path.exists(png_path):
            break
    else:
        return None

    #  wait 5 seconds for end of file writing by discrete intervals of 0.1 sec
    mtime = os.stat(png_path).st_mtime
    for _ in range(10 * 5):
        sleep(0.1)
        delta = os.stat(png_path).st_mtime - mtime
        if delta == 0:
            with open(png_path, "rb") as file:
                b_read = file.read()
            os.remove(png_path)
            os.remove(svg_path)
            return b_read
        else:
            mtime += delta
    else:
        return None


# =======================
try:
    SVG_OK = True
    if not sys.platform.startswith('win'):
        # LINUX

        import cairosvg
        # define svg2png() as cairosvg.svg2png() wrapper
        def svg2png(bytes_svg: bytes):
            """ Converts SVG bytes to PNG bytes on Linux by cairosvg
            """
            return cairosvg.svg2png(bytes_svg)
    else:
        # WINDOWS

        # workaround:  define svg2png() as alias of _svg2png_inkscape()
        svg2png = _svg2png_inkscape

    # test
    assert svg2png(SVG_SAMPLE)
    print("SVG - OK")
except Exception:
    # no way to convert SVG

    def svg2png(bytes_svg: bytes):
        """ Dummy converter """
        return None

    SVG_OK = False
    print("SVG - FAILED")
    print("-----traceback:-----")
    print(traceback.format_exc())
    print("--------------------")
