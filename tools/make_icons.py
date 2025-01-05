#!/usr/bin/env python
"""
Generates the Matplotlib icon, and toolbar icon images from the FontAwesome
font.

Generates SVG, PDF in one size (since they are vectors), and PNG in 24x24 and
48x48.
"""

import os
import tarfile
from argparse import ArgumentParser
from pathlib import Path
import urllib.request
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


# Set global plotting parameters for SVG and PDF output
mpl.rcdefaults()
mpl.rcParams['svg.fonttype'] = 'path'
mpl.rcParams['pdf.fonttype'] = 3
mpl.rcParams['pdf.compression'] = 9


# Function to download and cache the FontAwesome font
def download_fontawesome():
    font_url = "https://github.com/FortAwesome/Font-Awesome/archive/v4.7.0.tar.gz"
    cached_path = Path(mpl.get_cachedir(), "FontAwesome.otf")

    if not cached_path.exists():
        print("Downloading FontAwesome font...")
        with urllib.request.urlopen(font_url) as response, \
                tarfile.open(fileobj=response, mode="r:gz") as archive:
            font_file = archive.extractfile(
                archive.getmember("Font-Awesome-4.7.0/fonts/FontAwesome.otf"))
            with open(cached_path, 'wb') as out_file:
                out_file.write(font_file.read())
        print(f"FontAwesome font cached at {cached_path}")
    return cached_path


# Function to generate an individual icon
def generate_icon(font_path, unicode_char):
    fig = plt.figure(figsize=(1, 1))
    fig.patch.set_alpha(0.0)
    fig.text(0.5, 0.5, chr(unicode_char), ha='center', va='center',
             font=font_path, fontsize=72)
    return fig


# Function to generate the Matplotlib logo
def generate_matplotlib_icon():
    fig = plt.figure(figsize=(1, 1))
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0.025, 0.025, 0.95, 0.95], projection='polar')
    ax.set_axisbelow(True)

    N = 7
    arc = 2 * np.pi
    theta = np.arange(0, arc, arc / N)
    radii = 10 * np.array([0.2, 0.6, 0.8, 0.7, 0.4, 0.5, 0.8])
    width = np.pi / 4 * np.array([0.4, 0.4, 0.6, 0.8, 0.2, 0.5, 0.3])
    bars = ax.bar(theta, radii, width=width, bottom=0.0, linewidth=1,
                  edgecolor='k')

    for r, bar in zip(radii, bars):
        bar.set_facecolor(mpl.cm.jet(r / 10))

    ax.set_yticks(np.arange(1, 9, 2))
    ax.set_rmax(9)
    ax.tick_params(labelleft=False, labelright=False,
                   labelbottom=False, labeltop=False)
    ax.grid(lw=0.0)

    return fig


# Function to save the generated icon in multiple formats
def save_icon(fig, dest_dir, icon_name, add_black_fg_color=False):
    if add_black_fg_color:
        # Add explicit black foreground color to monochromatic svg icons
        # to ensure dark theme support
        svg_bytes_io = BytesIO()
        fig.savefig(svg_bytes_io, format='svg')
        svg = svg_bytes_io.getvalue()
        before, sep, after = svg.rpartition(b'\nz\n"')
        svg = before + sep + b' style="fill:black;"' + after
        (dest_dir / (icon_name + '.svg')).write_bytes(svg)
    else:
        fig.savefig(dest_dir / (icon_name + '.svg'))

    # Save as PDF
    fig.savefig(dest_dir / (icon_name + '.pdf'))

    # Save as PNG (24x24 and 48x48)
    for dpi, suffix in [(24, ''), (48, '_large')]:
        fig.savefig(dest_dir / (icon_name + suffix + '.png'), dpi=dpi)


# Function to create icons from the list of unicode characters
def create_icons(font_path, dest_dir, icon_defs):
    for name, unicode_char in icon_defs:
        print(f"Generating icon for '{name}'...")
        fig = generate_icon(font_path, unicode_char)
        save_icon(fig, dest_dir, name, add_black_fg_color=True)


# Function to generate the Matplotlib logo
def create_matplotlib_icon(dest_dir):
    print("Generating Matplotlib logo...")
    fig = generate_matplotlib_icon()
    save_icon(fig, dest_dir, 'matplotlib', add_black_fg_color=False)


# Main function to parse arguments and start the icon generation process
def main():
    parser = ArgumentParser(description="Generate Matplotlib icons and toolbar icons.")
    parser.add_argument(
        "-d", "--dest-dir",
        type=Path,
        default=Path(__file__).parent / "../lib/matplotlib/mpl-data/images",
        help="Directory to store the generated icons.")
    args = parser.parse_args()

    # Ensure destination directory exists
    dest_dir = args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Unicode characters for FontAwesome icons
    icon_defs = [
        ('home', 0xf015),
        ('back', 0xf060),
        ('forward', 0xf061),
        ('zoom_to_rect', 0xf002),
        ('move', 0xf047),
        ('filesave', 0xf0c7),
        ('subplots', 0xf1de),
        ('qt4_editor_options', 0xf201),
        ('help', 0xf128),
    ]

    # Download the FontAwesome font if not cached
    font_path = download_fontawesome()

    # Create icons
    create_icons(font_path, dest_dir, icon_defs)

    # Create Matplotlib logo
    create_matplotlib_icon(dest_dir)

    print("Icon generation complete!")


# Run the main function if this script is executed
if __name__ == "__main__":
    main()
