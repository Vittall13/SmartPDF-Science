"""Original PaddleOCR-VL script - Basic PDF to Markdown conversion.

Базовая версия из исходного PDF документа.
"""
import os
os.environ["PADDLE_USE_CUDNN"] = "0"
from paddleocr import PaddleOCRVL
from pathlib import Path
import time

# Папки проекта
INPUT_DIR = Path(r"input_pdfs")
OUTPUT_DIR = Path(r"output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Загрузка PaddleOCR-VL на GPU...")
start = time.time()

# Инициализация модели
vl = PaddleOCRVL(
    use_layout_detection=True,  # True = точная структура, False = быстрее
    format_block_content=True,  # обязательно для Markdown
    use_doc_orientation_classify=True,  # исправление поворотов
    use_doc_unwarping=False,  # False = сильно ускоряет
    device="gpu:0"
)

print(f"Загрузка заняла {time.time() - start:.1f} секунд\n")

# Обработка всех PDF в папке
for pdf_path in INPUT_DIR.glob("*.pdf"):
    print(f"\nОбрабатываю: {pdf_path.name}")
    start_file = time.time()
    
    try:
        results = vl.predict(str(pdf_path))
        
        md_parts = []
        images_saved = 0
        
        for page_num, res in enumerate(results, 1):
            # Основной Markdown-текст страницы
            if hasattr(res, 'markdown') and 'markdown_texts' in res.markdown:
                md_text = res.markdown['markdown_texts'].strip()
                md_parts.append(f"<!-- Страница {page_num} -->\n\n{md_text}")
            
            # Сохранение изображений, если они извлечены
            if hasattr(res, 'markdown') and 'markdown_images' in res.markdown:
                for rel_path, img in res.markdown['markdown_images'].items():
                    save_path = OUTPUT_DIR / "images" / pdf_path.stem / rel_path
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(save_path)
                    images_saved += 1
                    print(f"  Изображение сохранено: {save_path}")
        
        # Сборка и сохранение итогового файла
        if md_parts:
            full_md = "\n\n---\n\n".join(md_parts)
            out_file = OUTPUT_DIR / f"{pdf_path.stem}_gpu.md"
            out_file.write_text(full_md, encoding="utf-8")
            print(f"Готово за {time.time() - start_file:.1f} сек → {out_file}")
            
            if images_saved > 0:
                print(f"Сохранено изображений: {images_saved}")
        else:
            print("Markdown-текст не найден на страницах")
    
    except Exception as e:
        print(f"Ошибка при обработке {pdf_path.name}: {e}")

print("\nОбработка завершена.")