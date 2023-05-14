from io import BytesIO, StringIO

import cairosvg
from svgpathtools import svg2paths2, disvg
from svgpathtools.path import Path
from PIL import Image

from svg_to_paths import svg2paths2
from svg2anima import svg2animation_shell


def svg2png(paths, attributes, svg_attributes):
    drw = disvg(
        paths=paths,
        attributes=attributes,
        svg_attributes=svg_attributes,
        paths2Drawing=True,
    )
    svg_file = StringIO()
    drw.write(svg_file)

    svg_file = BytesIO(svg_file.getvalue().encode('utf-8'))
    png_file = BytesIO()
    cairosvg.svg2png(
        file_obj=svg_file,
        write_to=png_file,
    )
    return png_file


@svg2animation_shell
def svg2animation(input_file, output_file):
    paths, attributes, svg_attributes = svg2paths2(input_file)
    frames = []
    for path_index in range(len(paths)):
        new_attributes = attributes[:path_index+1]
        new_attributes[-1]['fill-opacity'] = 0
        fill = new_attributes[-1].get('fill')
        if fill:
            del new_attributes[-1]['fill']

        for line_index in range(len(paths[path_index])+1):
            if line_index == len(paths[path_index]):
                line_index -= 1
                del new_attributes[-1]['fill-opacity']
                if fill:
                    new_attributes[-1]['fill'] = fill

            new_paths = (
                paths[:path_index]
                + [Path(*paths[path_index][:line_index+1])]
            )
            png_file = svg2png(
                new_paths,
                new_attributes,
                svg_attributes,
            )
            frames.append(Image.open(png_file))

    if not frames:
        print('    empty')
        return

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=250,
        loop=0,
    )









"""
from svgutils.compose import *

CONFIG["svg.file_path"] = "files"
CONFIG["image.file_path"] = "result"

Figure(
    "10cm",
    "5cm",
    #SVG("Flag_of_Kaltan.svg").scale(0.2),
    SVG("Star_of_David.svg").scale(2),
    #Image(
    #    120,
    #    120,
    #    "lion.jpeg",
    #).move(120, 0),
).save("result/compose_example.svg")
"""


"""
from svgmanip import Element

output = Element(384, 356)

skip = Element('files/Flag_of_Kaltan.svg')#.rotate(-5)
attack = Element('files/Star_of_David.svg')#.rotate(5)

output.placeat(skip, 107.81, 8.76)
output.placeat(attack, 170.9, 0.08)

output.dump('result/output.svg')
output.save_as_png('result/output.png', 1024)
"""
