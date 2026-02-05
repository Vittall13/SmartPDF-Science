"""Original PaddleOCR-VL script - With page annotations.

Версия с аннотациями блоков на изображениях страниц.
"""
import os
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCRVL

# ────────────────────────────────────────────────
# Настройки
# ────────────────────────────────────────────────
INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output"
ANNOTATED_DIR = os.path.join(OUTPUT_DIR, "annotated")
POPPLER_PATH = None

COLOR_MAP = {
    "doc_title": (255, 0, 0),
    "paragraph_title": (0, 0, 255),
    "text": (0, 200, 0),
    "image": (0, 255, 255),
    "table": (255, 165, 0),
    "default": (200, 200, 200)
}

FONT_SIZE = 32
LINE_WIDTH = 6
FILL_ALPHA = 50

MIN_AREA = 5000  # минимальная площадь bbox (пиксели²)
MIN_TEXT_LEN = 15  # минимальная длина текста в блоке
MIN_SCORE = 0.65  # минимальный confidence

ADD_ANN_TO_MD = True
ANN_ONLY_MAJOR = True  # True = номера только для заголовков, таблиц, изображений


def ensure_directories():
    for d in [INPUT_DIR, OUTPUT_DIR, ANNOTATED_DIR]:
        os.makedirs(d, exist_ok=True)


def get_page_image(pdf_path: str, page_number: int):
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(
            pdf_path,
            first_page=page_number,
            last_page=page_number,
            poppler_path=POPPLER_PATH
        )
        return images[0]
    except Exception as e:
        print(f"pdf2image failed: {e}")
        return None


def get_model_image_size(inner_res):
    w = inner_res.get('width')
    h = inner_res.get('height')
    if w is not None and h is not None:
        return int(w), int(h)
    return 1024, 1024


def filter_and_merge_blocks(blocks):
    """Фильтруем мелкие/низкоскорные блоки и пытаемся объединить соседние text"""
    filtered = []
    i = 0
    
    while i < len(blocks):
        block = blocks[i]
        label = block.get("block_label", block.get("label", "unk"))
        score = block.get("block_score") or block.get("score", 1.0)
        bbox = block.get("block_bbox") or block.get("coordinate")
        text = block.get("block_content", "")
        
        # Пропускаем мелкие / низкоскорные
        if score < MIN_SCORE:
            i += 1
            continue
        
        if bbox is not None:
            if isinstance(bbox, np.ndarray):
                bbox = bbox.flatten().tolist()
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) if len(bbox) >= 4 else 0
            if area < MIN_AREA and len(text) < MIN_TEXT_LEN:
                i += 1
                continue
        
        # Пытаемся объединить с предыдущим text-блоком
        if filtered and label in ("text", "paragraph") and \
           filtered[-1].get("block_label", "") in ("text", "paragraph"):
            prev = filtered[-1]
            prev_bbox = prev.get("block_bbox") or prev.get("coordinate")
            
            if prev_bbox and len(prev_bbox) >= 4 and len(bbox) >= 4:
                # Если блоки близко (вертикально) — объединяем
                if abs(prev_bbox[1] - bbox[1]) < 50 and abs(prev_bbox[3] - bbox[1]) < 100:
                    prev["block_content"] = (prev.get("block_content", "") + " " + text).strip()
                    # Обновляем bbox
                    prev_bbox[0] = min(prev_bbox[0], bbox[0])
                    prev_bbox[1] = min(prev_bbox[1], bbox[1])
                    prev_bbox[2] = max(prev_bbox[2], bbox[2])
                    prev_bbox[3] = max(prev_bbox[3], bbox[3])
                    i += 1
                    continue
        
        filtered.append(block)
        i += 1
    
    return filtered


def draw_blocks(img: Image.Image, blocks: list, is_parsing: bool = True,
                scale_x: float = 1.0, scale_y: float = 1.0):
    draw = ImageDraw.Draw(img, "RGBA")
    try:
        font = ImageFont.truetype("arial.ttf", FONT_SIZE)
    except:
        font = ImageFont.load_default()
    
    for i, block in enumerate(blocks):
        label = block.get("block_label", block.get("label", "unk"))
        bbox_raw = block.get("block_bbox") or block.get("coordinate")
        order = i + 1
        
        if bbox_raw is None:
            continue
        
        if isinstance(bbox_raw, np.ndarray):
            bbox = bbox_raw.flatten().tolist()
        else:
            bbox = bbox_raw
        
        bbox_scaled = [
            int(coord * scale_x if j % 2 == 0 else coord * scale_y)
            for j, coord in enumerate(bbox)
        ]
        
        color = COLOR_MAP.get(label, COLOR_MAP["default"])
        
        if len(bbox_scaled) == 4:
            x1, y1, x2, y2 = bbox_scaled
            draw.rectangle(
                (x1, y1, x2, y2),
                outline=color + (255,),
                width=LINE_WIDTH,
                fill=color + (FILL_ALPHA,)
            )
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
        elif len(bbox_scaled) == 8:
            points = [(bbox_scaled[j], bbox_scaled[j+1]) for j in range(0, 8, 2)]
            draw.polygon(
                points,
                outline=color + (255,),
                width=LINE_WIDTH,
                fill=color + (FILL_ALPHA,)
            )
            xs, ys = [p[0] for p in points], [p[1] for p in points]
            center_x, center_y = sum(xs) // len(xs), sum(ys) // len(ys)
        else:
            continue
        
        text = f"{order} {label}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        tx = center_x - tw // 2
        ty = center_y - th // 2
        
        draw.rectangle((tx-12, ty-10, tx+tw+12, ty+th+10), fill=(0, 0, 0, 180))
        draw.text((tx, ty), text, fill=(255, 255, 255), font=font)


def add_annotation_comments(md_content: str, parsing_blocks: list) -> str:
    if not ADD_ANN_TO_MD or not parsing_blocks:
        return md_content
    
    lines = md_content.splitlines()
    new_lines = []
    block_idx = 0
    
    for line in lines:
        new_lines.append(line)
        stripped = line.strip()
        
        if ANN_ONLY_MAJOR:
            # Только значимые блоки
            if stripped.startswith('#') or stripped.startswith('![') or \
               stripped.startswith('|') or '```' in stripped:
                if block_idx < len(parsing_blocks):
                    ann_num = block_idx + 1
                    label = parsing_blocks[block_idx].get("block_label", "unk")
                    new_lines.append(f"<!-- ann: {ann_num} | {label} -->")
                    block_idx += 1
        else:
            # Все блоки
            if stripped and not stripped.startswith('<!--'):
                if block_idx < len(parsing_blocks):
                    ann_num = block_idx + 1
                    label = parsing_blocks[block_idx].get("block_label", "unk")
                    new_lines.append(f"<!-- ann: {ann_num} | {label} -->")
                    block_idx += 1
    
    return '\n'.join(new_lines)


def process_file(pipeline, pdf_name: str):
    pdf_path = os.path.join(INPUT_DIR, pdf_name)
    print(f"Обрабатываю: {pdf_path}")
    start = time.time()
    
    try:
        output = pipeline.predict(input=pdf_path)
        pages_res = list(output)
        print(f"  → Получено страниц: {len(pages_res)}")
        
        structured = pipeline.restructure_pages(
            pages_res,
            merge_tables=True,
            relevel_titles=True,
            concatenate_pages=True
        )
        
        stem = Path(pdf_name).stem
        md_path = os.path.join(OUTPUT_DIR, f"{stem}.md")
        structured[0].save_to_markdown(save_path=md_path)
        
        # Добавляем аннотации в MD
        if ADD_ANN_TO_MD:
            parsing_all = []
            for res in pages_res:
                inner = res.json.get('res', {})
                parsing = inner.get("parsing_res_list", [])
                filtered_parsing = filter_and_merge_blocks(parsing)
                parsing_all.extend(filtered_parsing)
            
            if parsing_all:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                enriched = add_annotation_comments(content, parsing_all)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(enriched)
                print(f"  Добавлены номера аннотаций в MD → {md_path}")
        
        # Аннотации на изображении
        for page_idx, res in enumerate(pages_res):
            page_img = get_page_image(pdf_path, page_idx + 1)
            if page_img is None:
                continue
            
            orig_w, orig_h = page_img.size
            inner = res.json.get('res', {})
            model_w, model_h = get_model_image_size(inner)
            scale_x = orig_w / model_w
            scale_y = orig_h / model_h
            
            print(f"  Масштаб: x={scale_x:.3f}, y={scale_y:.3f}")
            
            draw_img = page_img.copy()
            parsing = inner.get("parsing_res_list", [])
            
            if parsing:
                filtered = filter_and_merge_blocks(parsing)
                print(f"  → parsing_res_list после фильтрации: {len(filtered)} блоков")
                draw_blocks(draw_img, filtered, True, scale_x, scale_y)
                
                out_path = os.path.join(ANNOTATED_DIR, f"{stem}_p{page_idx+1}_ann.jpg")
                draw_img.save(out_path, quality=92)
                print(f"  Сохранено: {out_path}")
    
    except Exception as e:
        print(f"  Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"  Завершено за {time.time() - start:.1f} сек\n")


def main():
    ensure_directories()
    
    print("Инициализация PaddleOCR-VL...")
    pipeline = PaddleOCRVL()
    
    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print(f"PDF-файлы в '{INPUT_DIR}' не найдены.")
        return
    
    for pdf in pdfs:
        process_file(pipeline, pdf)
    
    print("Готово!")
    print(f"Markdown (с номерами аннотаций) → {Path(OUTPUT_DIR).resolve()}")
    print(f"Аннотированные изображения → {Path(ANNOTATED_DIR).resolve()}")


if __name__ == "__main__":
    main()