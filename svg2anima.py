import os.path
from argparse import ArgumentParser

import cairosvg

from main_variant2 import calculate_final_values, frame_iterator, get_frame_packer


def svg2animation(input_file, output_file, packer_name, fps, duration=None, width=None, height=None):
    # do SVG structure more simple
    simple_svg = cairosvg.svg2svg(
        file_obj=input_file,
        write_to=None,
    )
    scale, final_width, final_height = calculate_final_values(simple_svg, width, height)
    if duration:
        frames = []
        for frame in frame_iterator(simple_svg, scale):
            frames.append(frame)

        fps = len(frames) // duration
        packer = get_frame_packer(packer_name, output_file, fps, final_width, final_height)
        for frame in frames:
            packer.add(frame)
    else:
        packer = get_frame_packer(packer_name, output_file, fps, final_width, final_height)
        for frame in frame_iterator(simple_svg, scale):
            packer.add(frame)

    packer.finish()


if __name__ == '__main__':
    parser = ArgumentParser(
        description=(
            'This program converts svg picture to gif animation. You can only fps or duration.'
            'You can only width, height or no one'
        )
    )
    parser.add_argument('input_files', nargs='+')
    parser.add_argument('output_dir', nargs=1)
    parser.add_argument('--fps', type=int, default=24, help='frames per second')
    parser.add_argument('--duration', type=int, default=None, help='duration, seconds')
    parser.add_argument('--width', type=int, default=None, help='width of video, pixels')
    parser.add_argument('--height', type=int, default=None, help='height of video, pixels')
    parser.add_argument('--packer', type=str, default='opencv')
    args = parser.parse_args()
    for input_file_path in args.input_files:
        print('Processing:', input_file_path)
        file_name = os.path.basename(input_file_path)
        output_file_path = os.path.join(args.output_dir[0], f'{file_name}.gif')
        with open(input_file_path, 'rb') as input_file, open(output_file_path, 'wb') as output_file:
            svg2animation(input_file, output_file, args.packer, args.fps, args.duration, args.width, args.height)
            print('Ready')
            print()
