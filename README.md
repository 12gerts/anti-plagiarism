# Python-антиплагиат
Консольная утилита, которая определяет похожесть 2 python-скриптов

## Запуск
Для запуска необходимо ввести в командной строке
```sh
python3 compare.py [list_of_input_files] [output_file]
```
* `[list_of_input_files]` - файл с указанием скриптов для анализа
* `[output_file]` - выходной файл с результатами анализа

### Пример запуска
```sh
python3 compare.py input.txt scores.txt
```
### Пример входного файла
```
files/main.py plagiat1/main.py
files/loss.py plagiat2/loss.py
files/loss.py files/loss.py
```
## Реализация
Для предобработки текста используется библиотека `ast`: 
* Строится абстрактное синтаксическое дерево
* Удаляется документация и комментарии
* Если названия переменных похожи, то они приводятся к одному виду  

Далее схожесть текстов определяется по расстоянию Левенштейна, которое нормализуется 
на длину текста