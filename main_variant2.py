import os.path
from io import BytesIO, StringIO
from xml.dom.minidom import parse

import cairosvg
import tinycss2
from svgpathtools import svg2paths2, disvg
from svgpathtools.path import Path
from PIL import Image, ImageDraw, ImageFont

import cv2
import numpy as np

from svg_to_paths import svg2paths2


class OpenCVP2V:
    """OpenCV pictures to video converter"""

    def __init__(self, output_filename, fps, width, height):
        _, ext = os.path.splitext(output_filename)
        if ext == '.avi':
            fourcc_str = 'MJPG'
        elif ext == '.png':
            fourcc_str = 'WEBP'
        elif ext == '.webp':
            fourcc_str = 'WEBP'
        elif ext in ('.mp4v', '.mp4'):
            fourcc_str = 'XVID'
        elif ext == '.wmv':
            fourcc_str = 'MP42'
        else:
            raise Exception(f'unsupported extension: {ext}')

        # fourcc = cv2.VideoWriter_fourcc(*'X264')

        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        self.video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    def add(self, frame):
        """
        :param frame: image binary data (png, webp, etc)
        """
        image_bytes = bytearray(frame.getvalue())
        image_np = np.asarray(image_bytes, dtype='uint8')
        image_frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        self.video_writer.write(image_frame)

    def finish(self):
        self.video_writer.release()


class GIFP2V:
    """GIF pictures to video converter"""

    def __init__(self, output_file, fps, width, height):
        self.frames = []
        self.output_file = output_file
        self.fps = fps

    def add(self, frame):
        """
        :param frame: image binary data (png, webp, etc)
        """
        image = Image.open(frame)
        # ------>
        # name = '{}-{}'.format(str(path_index).rjust(4, '0'), str(line_index).rjust(4, '0'))
        # with open(f'png/{name}.png', 'wb') as f:
        #     f.write(png_file.getvalue())

        # fnt = ImageFont.truetype(size=40)
        # draw = ImageDraw.Draw(image)
        # fnt = draw.getfont()
        # draw.text((70, 70), name, font=fnt)
        # <------
        self.frames.append(image)

    def finish(self):
        if self.frames:
            self.frames[0].save(
                self.output_file,
                save_all=True,
                append_images=self.frames[1:],
                optimize=True,
                duration=int(1000 / self.fps),
                loop=0,
                disposal=1,
            )


def svg_data2png(paths, attributes, svg_attributes, scale: float):
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
        scale=scale,
    )
    return png_file


def unset_attributes(attributes):
    only_background = False
    # source_attributes = attributes.copy()
    source_attributes = {}

    source_fill_opacity = attributes.get('fill-opacity')
    if source_fill_opacity is not None:
        source_attributes['fill-opacity'] = source_fill_opacity
    attributes['fill-opacity'] = 0

    source_fill = attributes.get('fill')
    if source_fill is not None:
        source_attributes['fill'] = source_fill
    attributes['fill'] = 'none'

    source_style = attributes.get('style')
    if source_style is not None:
        source_attributes['style'] = source_style
        rules = tinycss2.parse_declaration_list(source_style, skip_whitespace=True)

        fill_color = None
        stroke_color = None
        for rule in rules:
            if rule.name == 'fill-opacity':
                rule.value = [
                    tinycss2.ast.NumberToken(line=None, column=None, value=None, int_value=None, representation='0')]
            elif rule.name == 'fill':
                fill_color = tinycss2.serialize(rule.value)
                if fill_color == stroke_color:
                    only_background = True
            elif rule.name == 'stroke':
                stroke_color = tinycss2.serialize(rule.value)
                if fill_color == stroke_color or stroke_color == 'none':
                    only_background = True

        attributes['style'] = tinycss2.serialize(rules)

    return only_background, source_attributes


def calculate_scale(svg_str, final_value: int, field_name: str):
    """
    Cite:
    "One point is the equivalent of 1.333(3) pixels. On the other hand, one pixel is the equivalent of 0.75 points."
    Source: https://simplecss.eu/pxtoems.html

    :param svg_str: svg, which has width and height in pt
    :param final_value: width or height in px
    :param field_name: calculate by what field: "width" or "height"
    :return: tuple like (scale to transform svg, final width and final height)
    """
    dom_svg = parse(svg_str)
    source_width = float(dom_svg.childNodes[0].attributes.get('width').value[:-2])
    source_height = float(dom_svg.childNodes[0].attributes.get('height').value[:-2])

    if field_name not in ('width', 'height'):
        raise Exception(f'invalid `field_name`: {field_name}')

    if field_name == 'width':
        scale = (final_value * 0.75) / source_width
        return scale, final_value, int(source_height * 1.3333333333333333 * scale)
    else:
        scale = (final_value * 0.75) / source_height
        return scale, int(source_width * 1.3333333333333333 * scale), final_value


def calculate_source_size(svg_str):
    dom_svg = parse(svg_str)
    source_width = float(dom_svg.childNodes[0].attributes.get('width').value[:-2])
    source_height = float(dom_svg.childNodes[0].attributes.get('height').value[:-2])
    return int(source_width * 1.3333333333333333), int(source_height * 1.3333333333333333)



def svg2animation(input_file, output_file, fps, width=None, height=None):
    simple_svg = cairosvg.svg2svg(
        file_obj=input_file,
        write_to=None,
    )
    simple_svg_io = BytesIO(simple_svg)
    if width is not None:
        scale, final_width, final_height = calculate_scale(simple_svg_io, width, 'width')
    elif height is not None:
        scale, final_width, final_height = calculate_scale(simple_svg_io, height, 'height')
    else:
        scale = 1
        final_width, final_height = calculate_source_size(simple_svg_io)

    paths, attributes, svg_attributes = svg2paths2(BytesIO(simple_svg))

    # converter = OpenCVP2V('1output.wmv', fps, final_width, final_height)
    converter = GIFP2V(output_file, fps, final_width, final_height)
    for path_index in range(len(paths)):
        new_attributes = attributes[:path_index+1]
        only_background, source_attributes = unset_attributes(new_attributes[-1])
        for line_index in range(len(paths[path_index])+1):
            if only_background:
                line_index = len(paths[path_index])

            if line_index == len(paths[path_index]):
                line_index -= 1
                new_attributes[-1].update(source_attributes)

            new_paths = (
                paths[:path_index]
                + [Path(*paths[path_index][:line_index+1])]
            )
            png_file = svg_data2png(
                new_paths,
                new_attributes,
                svg_attributes,
                scale=scale,
            )
            converter.add(png_file)

            if only_background:
                break

    converter.finish()
