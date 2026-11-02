# Служебная ветка

Здесь сборщик и тесты. Готовый скрипт и инструкция лежат в ветке `main`.

## Сборка

```bash
python3 build.py Icon-V-and-P-Series-Ableton-Script-v1.16-ZIP.zip
```

Сборщик берёт официальный архив iCON, вносит правки и кладёт результат в `build/`. Если в новой версии iCON правка не подойдёт, сборка остановится.

## Тесты

В `orig/` должен лежать распакованный официальный архив.

```bash
python3 -B test/harness.py build Icon_V_and_P_Series_Ableton_Follow  # основные сценарии
python3 -B test/fuzz.py build 1 x+m+x+x 300                          # случайные действия
python3 -B test/compare.py orig build 3 200                          # сравнение с оригиналом на всех схемах
python3.11 -B test/real_framework.py build                           # настоящий _Framework из Live 12
```

Live API в тестах ненастоящий, а контроллеров и экранов в них нет.

## Утилиты для macOS

- `swift tools/color_test.swift` показывает цвета и надписи на контроллере.
- `tools/p1watch.swift` пишет в лог, когда контроллер отключается от USB.

## Публикация

Скопировать содержимое `build/` в ветку `main`, обновить там README и запушить.
