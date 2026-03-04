from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def generate_method_diagram(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 220
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    boxes = [
        (30, 70, 180, 150, "Input"),
        (250, 70, 400, 150, "Model"),
        (470, 70, 620, 150, "Training"),
        (690, 70, 840, 150, "Output"),
    ]

    for x1, y1, x2, y2, label in boxes:
        draw.rectangle((x1, y1, x2, y2), outline="black", width=2)
        draw.text((x1 + 45, y1 + 30), label, fill="black")

    arrows = [((180, 110), (250, 110)), ((400, 110), (470, 110)), ((620, 110), (690, 110))]
    for (x1, y1), (x2, y2) in arrows:
        draw.line((x1, y1, x2, y2), fill="black", width=2)
        draw.polygon([(x2 - 10, y2 - 6), (x2, y2), (x2 - 10, y2 + 6)], fill="black")

    image.save(output_path)
