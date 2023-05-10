from io import BytesIO, StringIO

import cairosvg
from svgpathtools import svg2paths2, disvg
from svgpathtools.path import Path
from PIL import Image, ImageDraw, ImageFont
import tinycss2

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
    with open('middle.svg', 'wb') as f:
        f.write(_file_path)

    _file_path = BytesIO(_file_path)

    paths, attributes, svg_attributes = svg2paths2(_file_path)

    frames = []
    for path_index in range(len(paths)):
        new_attributes = attributes[:path_index+1]
        only_background = False

        # source_attributes = new_attributes[-1].copy()
        source_fill_opacity = new_attributes[-1].get('fill-opacity')
        new_attributes[-1]['fill-opacity'] = 0
        source_fill = new_attributes[-1].get('fill')
        new_attributes[-1]['fill'] = 'none'

        source_style = new_attributes[-1].get('style')
        if source_style:
            rules = tinycss2.parse_declaration_list(source_style, skip_whitespace=True)

            fill_color = None
            stroke_color = None
            for rule in rules:
                if rule.name == 'fill-opacity':
                    rule.value = [tinycss2.ast.NumberToken(line=None, column=None, value=None, int_value=None, representation='0')]
                elif rule.name == 'fill':
                    fill_color = tinycss2.serialize(rule.value)
                    if fill_color == stroke_color:
                        print('--')
                        only_background = True
                elif rule.name == 'stroke':
                    stroke_color = tinycss2.serialize(rule.value)
                    if fill_color == stroke_color or stroke_color == 'none':
                        print('--')
                        only_background = True

            new_attributes[-1]['style'] = tinycss2.serialize(rules)

        for line_index in range(len(paths[path_index])+1):
            if only_background:
                line_index = len(paths[path_index])

            if line_index == len(paths[path_index]):
                line_index -= 1

                if source_fill_opacity is not None:
                    new_attributes[-1]['fill-opacity'] = source_fill_opacity

                if source_fill is not None:
                    new_attributes[-1]['fill'] = source_fill

                if source_style is not None:
                    new_attributes[-1]['style'] = source_style

            new_paths = (
                paths[:path_index]
                + [Path(*paths[path_index][:line_index+1])]
            )
            png_file = svg2png(
                new_paths,
                new_attributes,
                svg_attributes,
            )
            image = Image.open(png_file)
            # ------>
            # name = '{}-{}'.format(str(path_index).rjust(4, '0'), str(line_index).rjust(4, '0'))
            # with open(f'png/{name}.png', 'wb') as f:
            #     f.write(png_file.getvalue())

            # fnt = ImageFont.truetype(size=40)
            # draw = ImageDraw.Draw(image)
            # fnt = draw.getfont()
            # draw.text((70, 70), name, font=fnt)
            # <------
            frames.append(image)
            if only_background:
                break

    if not frames:
        print('    empty')
        return

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        optimize=True,
        duration=200,
        loop=0,
        disposal=1,
    )
