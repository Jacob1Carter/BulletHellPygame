import os
from PIL import Image


def refactor():
    for i in range(0, 31):
        img = Image.open(os.path.join("Assets", "Rocket_ico", f"Rocket{str(i)}.png"))
        img.save(os.path.join("Assets", "Warp_ico", f"Warp{str(i)}.png"))
