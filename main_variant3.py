from io import BytesIO, StringIO

import cairosvg
from svgpathtools import svg2paths2, disvg
from svgpathtools.path import Path
from PIL import Image

from svg_to_paths import svg2paths2




from cairosvg.parser import Tree
from cairosvg.surface import PNGSurface, SVGSurface
def go(node, depth=0):
    for child in node.children:
        print(' '*depth, child.tag, child)
        go(child, depth+1)


with open('files/Flag_of_South_Korea.svg', encoding='utf-8') as svg_file, open('result/output.svg', 'wb') as png_file:
    tree = Tree(file_obj=svg_file)
    output = BytesIO()
    # surface = PNGSurface(tree, dpi=96, output=output)
    # surface.draw(tree)
    # print(surface.images)
    # print(dir(surface))
    # go(tree)
    #
    # cairosvg.svg2png(
    #     file_obj=svg_file,
    #     # write_to='result/output{}.png'.format(name_postfix),
    #     write_to=png_file,
    # )
    from cairosvg.colors import negate_color
    from cairosvg.image import invert_image
    dpi = 96
    scale = 1
    parent_width = None
    parent_height = None
    output_width = None
    output_height = None
    negate_colors = False
    invert_images = False
    background_color = None
    instance = SVGSurface(
        tree, output, dpi, None, parent_width, parent_height, scale,
        output_width, output_height, background_color,
        map_rgba=negate_color if negate_colors else None,
        map_image=invert_image if invert_images else None)
    print(type(instance.output))
    instance.finish()
    png_file.write(output.getvalue())
