# MODU Bistro party platter poster (Store 2)

Generator for the A2 (420x594mm) + IG 4:5 (1080x1350) poster. Layout traced 1:1 from Seth's reference (v4/v5).

On the Mac (temp venv with pillow numpy playwright; `python -m playwright install chromium`):

    python src/clean_cutout.py DSC04392_cutout.png DSC04392_clean.png --grade [--erase "x,y x,y x,y"]
    python src/build.py out final photo DSC04392_clean.png      # PLATTER_W / PLATTER_BOTTOM env vars move the photo
    python src/render.py out/MODU-Bistro_party-platter_A2_final.svg out/A2.pdf
    python src/render.py out/MODU-Bistro_party-platter_IG-4x5_final.svg out/IG.jpg 1080
