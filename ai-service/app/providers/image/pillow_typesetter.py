import asyncio
import io
from PIL import Image, ImageDraw
from app.providers.image.font_loader import load_font


"""在擦除后的底图上，按 OCR 框自动字号/换行写入译文。"""
class PillowTypesetter:
    def _wrap_text(self, text: str, font, draw: ImageDraw.ImageDraw, max_width: int) -> list[str]:
        lines: list[str] = []
        current = ""
        for ch in text:
            trial = current + ch
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines or [""]

    def _fit_font_and_lines(self, text: str, draw: ImageDraw.ImageDraw, box_w: int, box_h: int):
        max_size = max(10, min(box_h, int(box_h * 0.85)))
        min_size = 8
        best = (load_font(min_size), [text], min_size)
        for size in range(max_size, min_size - 1, -1):
            font = load_font(size)
            lines = self._wrap_text(text, font, draw, max(1, box_w - 4))
            line_heights = []
            max_line_w = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_heights.append(bbox[3] - bbox[1])
                max_line_w = max(max_line_w, bbox[2] - bbox[0])
            spacing = max(1, size // 6)
            total_h = sum(line_heights) + spacing * max(0, len(lines) - 1)
            if max_line_w <= box_w - 2 and total_h <= box_h - 2:
                return font, lines, size, spacing, line_heights
            best = (font, lines, size)
        font, lines, size = best
        spacing = max(1, size // 6)
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        return font, lines, size, spacing, line_heights

    def _pick_color(self, image: Image.Image, x: int, y: int, w: int, h: int) -> tuple[int, int, int]:
        crop = image.crop((x, y, min(image.width, x + w), min(image.height, y + h))).convert("RGB")
        pixels = list(crop.getdata())
        if not pixels:
            return (20, 20, 20)
        avg = tuple(sum(c[i] for c in pixels) // len(pixels) for i in range(3))
        luminance = 0.299 * avg[0] + 0.587 * avg[1] + 0.114 * avg[2]
        return (245, 245, 245) if luminance < 140 else (20, 20, 20)

    def _compose_sync(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)
        for index, region in enumerate(regions):
            text = (translations[index] if index < len(translations) else "").strip()
            if not text:
                continue
            x, y = int(region["x"]), int(region["y"])
            w, h = max(1, int(region["width"])), max(1, int(region["height"]))
            font, lines, _size, spacing, line_heights = self._fit_font_and_lines(text, draw, w, h)
            color = self._pick_color(image, x, y, w, h)
            total_h = sum(line_heights) + spacing * max(0, len(lines) - 1)
            cursor_y = y + max(0, (h - total_h) // 2)
            for line, line_h in zip(lines, line_heights):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                cursor_x = x + max(0, (w - line_w) // 2)
                draw.text((cursor_x, cursor_y), line, font=font, fill=color)
                cursor_y += line_h + spacing
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    async def compose(self, image_bytes: bytes, regions: list[dict], translations: list[str]) -> bytes:
        return await asyncio.to_thread(self._compose_sync, image_bytes, regions, translations)
