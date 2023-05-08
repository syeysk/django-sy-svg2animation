"""This submodule contains tools for creating path objects from SVG files.
The main tool being the svg2paths() function."""

# External dependencies
from __future__ import division, absolute_import, print_function
from xml.dom.minidom import parse
import os
from io import StringIO
import re
try:
    from os import PathLike as FilePathLike
except ImportError:
    FilePathLike = str

# Internal dependencies
from svgpathtools.parser import parse_path
from svgpathtools.svg_to_paths import (
    ellipse2pathd,
    polyline2pathd,
    polygon2pathd,
    rect2pathd,
    line2pathd,
)


def dom2dict(element):
    """Converts DOM elements to dictionaries of attributes."""
    keys = list(element.attributes.keys())
    values = [val.value for val in list(element.attributes.values())]
    return dict(list(zip(keys, values)))


def all2pathd(
    doc,
    d_strings,
    attribute_dictionary_list,
    nodes_by_id,
    convert_circles_to_paths,
    convert_ellipses_to_paths,
    convert_lines_to_paths,
    convert_polylines_to_paths,
    convert_polygons_to_paths,
    convert_rectangles_to_paths,
):
    for node in doc.childNodes:
        try:
            tag_name = node.tagName
        except:
            continue

        dnode = dom2dict(node)
        pathd = None

        node_id = dnode.get('id')
        if node_id:
            print('  add', node_id, dnode)
            nodes_by_id[node_id] = node

        # Use minidom to extract path strings from input SVG
        if tag_name == 'path':
            pathd = dnode['d']

        # Use minidom to extract polyline strings from input SVG, convert to
        # path strings, add to list
        if convert_polylines_to_paths and tag_name == 'polyline':
            pathd = polyline2pathd(dnode)

        # Use minidom to extract polygon strings from input SVG, convert to
        # path strings, add to list
        if convert_polygons_to_paths and tag_name == 'polygon':
            pathd = polygon2pathd(dnode)

        if convert_lines_to_paths and tag_name == 'line':
            pathd = ('M' + dnode['x1'] + ' ' + dnode['y1'] +
                           'L' + dnode['x2'] + ' ' + dnode['y2'])

        if convert_ellipses_to_paths and tag_name == 'ellipse':
            pathd = ellipse2pathd(dnode)

        if convert_circles_to_paths and tag_name == 'circle':
            pathd = ellipse2pathd(dnode)

        if convert_rectangles_to_paths and tag_name == 'rect':
            pathd = rect2pathd(dnode)

        if tag_name == 'g':
            all2pathd(
                node,
                d_strings,
                attribute_dictionary_list,
                nodes_by_id,
                convert_circles_to_paths,
                convert_ellipses_to_paths,
                convert_lines_to_paths,
                convert_polylines_to_paths,
                convert_polygons_to_paths,
                convert_rectangles_to_paths,
            )

        if tag_name == 'use':
            node_id = dnode.get('xlink:href', '')[1:]
            print('  use', node_id, dnode)
            if node_id:
                all2pathd(
                    nodes_by_id[node_id],
                    d_strings,
                    attribute_dictionary_list,
                    nodes_by_id,
                    convert_circles_to_paths,
                    convert_ellipses_to_paths,
                    convert_lines_to_paths,
                    convert_polylines_to_paths,
                    convert_polygons_to_paths,
                    convert_rectangles_to_paths,
                )

        if pathd:
            d_strings.append(pathd)
            attribute_dictionary_list.append(dnode)

def svg2paths(svg_file_location,
              return_svg_attributes=False,
              convert_circles_to_paths=True,
              convert_ellipses_to_paths=True,
              convert_lines_to_paths=True,
              convert_polylines_to_paths=True,
              convert_polygons_to_paths=True,
              convert_rectangles_to_paths=True):
    # strings are interpreted as file location everything else is treated as
    # file-like object and passed to the xml parser directly
    from_filepath = isinstance(svg_file_location, str) or isinstance(svg_file_location, FilePathLike)
    svg_file_location = os.path.abspath(svg_file_location) if from_filepath else svg_file_location

    doc = parse(svg_file_location)

    d_strings = []
    attribute_dictionary_list = []
    nodes_by_id = {}

    pathd = all2pathd(
        doc.getElementsByTagName('svg')[0],
        d_strings,
        attribute_dictionary_list,
        nodes_by_id,
        convert_circles_to_paths,
        convert_ellipses_to_paths,
        convert_lines_to_paths,
        convert_polylines_to_paths,
        convert_polygons_to_paths,
        convert_rectangles_to_paths,
    )

    if return_svg_attributes:
        svg_attributes = dom2dict(doc.getElementsByTagName('svg')[0])
        doc.unlink()
        path_list = [parse_path(d) for d in d_strings]
        return path_list, attribute_dictionary_list, svg_attributes
    else:
        doc.unlink()
        path_list = [parse_path(d) for d in d_strings]
        return path_list, attribute_dictionary_list


def svg2paths2(svg_file_location,
               return_svg_attributes=True,
               convert_circles_to_paths=True,
               convert_ellipses_to_paths=True,
               convert_lines_to_paths=True,
               convert_polylines_to_paths=True,
               convert_polygons_to_paths=True,
               convert_rectangles_to_paths=True):
    """Convenience function; identical to svg2paths() except that
    return_svg_attributes=True by default.  See svg2paths() docstring for more
    info."""
    return svg2paths(svg_file_location=svg_file_location,
                     return_svg_attributes=return_svg_attributes,
                     convert_circles_to_paths=convert_circles_to_paths,
                     convert_ellipses_to_paths=convert_ellipses_to_paths,
                     convert_lines_to_paths=convert_lines_to_paths,
                     convert_polylines_to_paths=convert_polylines_to_paths,
                     convert_polygons_to_paths=convert_polygons_to_paths,
                     convert_rectangles_to_paths=convert_rectangles_to_paths)


def svgstr2paths(svg_string,
               return_svg_attributes=False,
               convert_circles_to_paths=True,
               convert_ellipses_to_paths=True,
               convert_lines_to_paths=True,
               convert_polylines_to_paths=True,
               convert_polygons_to_paths=True,
               convert_rectangles_to_paths=True):
    """Convenience function; identical to svg2paths() except that it takes the
    svg object as string.  See svg2paths() docstring for more
    info."""
    # wrap string into StringIO object
    svg_file_obj = StringIO(svg_string)
    return svg2paths(svg_file_location=svg_file_obj,
                     return_svg_attributes=return_svg_attributes,
                     convert_circles_to_paths=convert_circles_to_paths,
                     convert_ellipses_to_paths=convert_ellipses_to_paths,
                     convert_lines_to_paths=convert_lines_to_paths,
                     convert_polylines_to_paths=convert_polylines_to_paths,
                     convert_polygons_to_paths=convert_polygons_to_paths,
                     convert_rectangles_to_paths=convert_rectangles_to_paths)
