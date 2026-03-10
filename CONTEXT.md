# CONTEXT.md — SmartPDF-Science
> Этот файл предназначен для LLM (Claude, GPT, Perplexity и др.).
> Читай его ПЕРВЫМ при каждой новой сессии работы с проектом.

---

## Что это за проект

AI-инструмент для конвертации PDF → DOCX / LaTeX / Markdown / HTML.
Специализация: **научные документы** с формулами, таблицами, смешанными языками (RU + EN).

Архитектура: двухэтапный пайплайн.
- Stage 1: PaddleOCR-VL + PP-FormulaNet (GPU, CUDA) — OCR + распознавание формул в LaTeX
- Stage 2: Qwen3-8B — LLM постобработка и коррекция текста
- Интерфейсы: Gradio UI + FastAPI REST

---

## Стек

| Слой | Технология | Версия |
|---|---|---|
| Python | Python | 3.11+ |
| GPU/CUDA | CUDA | 12.6 |
| OCR | PaddleOCR-VL + PaddleX | >=3.0 |
| Формулы | PP-FormulaNet_plus-L | paddlepaddle-gpu 3.2.1 |
| LLM | Qwen3-8B (HuggingFace) | transformers >=4.36 |
| API | FastAPI + Uvicorn | >=0.104 |
| UI | Gradio | >=4.0 |
| Экспорт | python-docx, pylatex, weasyprint | см. requirements.txt |

---

## Структура исходников

```
src/smartpdf/
├── core/
│   ├── ocr_engine.py        # главный OCR-движок (PaddleOCR-VL)
│   ├── formula_recognizer.py # PP-FormulaNet → LaTeX
│   ├── preprocessor.py      # предобработка изображений
│   └── postprocessor.py     # пост-нормализация структуры
├── llm/
│   ├── qwen_corrector.py    # Qwen3-8B коррекция текста
│   └── prompts.py           # системные промпты для LLM
├── exporters/               # DOCX / LaTeX / MD / HTML
├── api/fastapi_app.py       # REST API
└── ui/gradio_app.py         # Web UI
```

---

## Текущий статус (март 2026)

- **Стадия**: MVP заложен (структура, README, конфиги, Docker)
- **Последний коммит**: 07.02.2026 — `chore: update OCR formula toggle defaults`
- **Что реально работает**: неизвестно — код не проверялся с момента загрузки
- **Что НЕ реализовано / под вопросом**:
  - [ ] Реальное тестирование pipeline end-to-end
  - [ ] Проверка совместимости paddlepaddle-gpu 3.2.1 + CUDA 12.6 на целевом железе
  - [ ] Промпты в `llm/prompts.py` — требуют ревью и тонкой настройки
  - [ ] Тесты в `tests/` — созданы структурно, реальное покрытие неизвестно

---

## Приоритеты следующей сессии (заполняй перед каждой сессией)

> **Дата**: ___________
> **Цель сессии**: ___________
> **Конкретная задача для LLM**: ___________
> **Что нельзя трогать**: ___________

---

## Известные проблемы / риски

- `numpy==2.3.1` в requirements.txt — потенциальный конфликт с paddlepaddle-gpu 3.2.1 (Paddle исторически требует numpy < 2.0, проверить!)
- `poppler-utils` в pip — это системный пакет, не Python; нужен apt-get / системный менеджер пакетов
- Qwen3-8B требует ~16GB VRAM в fp16; при 20GB RTX 3080 остаётся мало места для OCR-моделей — возможна OOM ошибка при одновременной работе Stage 1 + Stage 2

---

## Как правильно ставить задачи LLM в этом проекте

1. **Всегда указывай контекст модуля**: "Работаем с `src/smartpdf/llm/qwen_corrector.py`"
2. **Указывай зависимости**: "Используем Qwen3-8B через HuggingFace transformers 4.36+"
3. **Запрашивай security-check**: "Проверь входные данные на path traversal / prompt injection перед передачей в LLM"
4. **Требуй версии зависимостей** при добавлении новых: "Укажи точную версию и возможные конфликты"
5. **Проси объяснение решения**, не только код: "Почему именно такой подход? Есть ли альтернативы?"

---

## Ссылки

- Репозиторий: https://github.com/Vittall13/SmartPDF-Science
- PaddleOCR-VL: https://huggingface.co/PaddlePaddle/PaddleOCR-VL
- Qwen3-8B: https://huggingface.co/Qwen/Qwen3-8B
- PP-FormulaNet: https://paddleocr.ai

---

## История сессий

| Дата | Что делали | Результат |
|---|---|---|
| 05–07.02.2026 | Первоначальная структура проекта | MVP scaffold, README, Docker, tests skeleton |
| ___.___.___ | | |
