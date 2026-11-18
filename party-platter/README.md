# MODU Bistro party platter poster (Store 2)

Generator for the A2 (420x594mm) + IG 4:5 (1080x1350) poster. Layout traced 1:1 from Seth's reference (v4/v5).

On the Mac (temp venv with pillow numpy playwright; `python -m playwright install chromium`):

    python src/clean_cutout.py DSC04392_cutout.png DSC04392_clean.png --grade [--erase "x,y x,y x,y"]
    python src/build.py out final photo DSC04392_clean.png      # PLATTER_W / PLATTER_BOTTOM env vars move the photo
    python src/render.py out/MODU-Bistro_party-platter_A2_final.svg out/A2.pdf
    python src/render.py out/MODU-Bistro_party-platter_IG-4x5_final.svg out/IG.jpg 1080

IG carousel (close-ups, 1080x1350, layered SVG per slide):

    python src/carousel.py spec.json carousel      # spec format in the header of carousel.py
    python src/render.py carousel/MODU-Bistro_party-platter_carousel_01.svg carousel/01.jpg 1080

Reshape the steamer toward the reference (shallow tray, higher camera):

    python src/warp_cutout.py DSC04392_clean.png shallow.png --wall <front wall px> --squash 0.35 [--vstretch 1.12] [--keystone 1.06]

Polish (colour match to the red background, defringe, light wrap) and placement extras:

    python src/finish_cutout.py warped.png final.png [--ev -0.15 --warm 0.5 --contrast 0.25 --vib 0.2 --split 0.35 --choke 1 --defringe 6 --wrap 0.35]
    GLOW=0.8 SHADOW=1 PLATTER_DX=0 PLATTER_W=880 PLATTER_BOTTOM=995 python src/build.py out final photo final.png
