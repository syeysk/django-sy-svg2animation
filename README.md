# Svg2animation

Here is are experimental scripts for making video from svg-pictures.

## Installing

Run this to install requirements:
```sh
pip3 install -r requirements.txt
```

For Windows you need to install [GTK3](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) and reload your computer.

## Using

Run tne command to convert svg-picture to gif-animates:

```sh
python3 svg2anima.py --fps 12 --width 1280 filename1.svg filenameN.svg dir_for_result
```

or

```sh
python3 svg2anima.py --fps 12 --height 680 filename1.svg filenameN.svg dir_for_result
```

The result will be saved in `dir_for_result` directory for every picture.

Real command, which I use for test:

```sh
python3 svg2anima.py --fps 12 --height 680 files/Flag_Of_Kaltan.svg result
```

## Drawing algorithm

Каждый контур — это ломанная линия либо дуга. Для упрощения назовём их линией.

1. Вынимаем линии
2. Вычисляем от линии точку, находящуюся выше и левее второй точки. Сохраняем все в список.
3. Список сортируем (горизонталь — слева направо, вертикаль — сверху вниз)
4.1 Для каждой линии генерируем промежуточные кадры (растущие линии).
4.1 Генерируем промежуточные кадры для мнимых линий, являющися движением руки от конца одной линии к началу следующей линии.
5. К концу линии каждого кадра добавляем изображение кисти руки с карандашом.
6. Преобразуем каждый кадр в PNG и упаковываем в GIF.

## Links

### Modules

Наслаивание руки на промежуточный кадр:
- https://github.com/btel/svg_utils
Получение и обработка линий из svg:
- https://pypi.org/project/svgpathtools/
Конвертация SVG в PNG, наслаивание SVG:
- https://github.com/CrazyPython/svgmanip
Генерация интерактивного SVG:
- https://docs.eyesopen.com/toolkits/python/depicttk/svg.html

### Lessons

Генерация GIF:
- https://python-scripts.com/create-gif-in-pil
