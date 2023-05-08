from io import BytesIO, StringIO

import cairosvg
from svgpathtools import svg2paths2, disvg
from svgpathtools.path import Path
from PIL import Image

from svg_to_paths import svg2paths2
from tools import svg2animation_shell


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
    _file_path = cairosvg.svg2svg(
        file_obj=input_file,
        write_to=None,
    )
    _file_path = BytesIO(_file_path)

    paths, attributes, svg_attributes = svg2paths2(_file_path)

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
