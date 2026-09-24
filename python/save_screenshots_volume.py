#!/usr/bin/env python3

"""
Create a 2x2 screenshot of a 3D NIfTI or MGZ volume.
The figure contains coronal, axial, and two sagittal views.
An optional binary mask can be displayed as a contour.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

from utils.viz import create_screenshot


def create_parser():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("subject",
                        help="Subject name to display as the figure title.")
    parser.add_argument("volume_filename",
                        help="Input 3D volume (.nii, .nii.gz, .mgz, or .mgh).")
    parser.add_argument("output_filename",
                        help="Output PNG filename.")
    parser.add_argument("--overlay", dest='overlay_filename',
                        help="Optional binary mask to display as a contour.")
    return parser


def load_volume(filename):
    """
    Load a NIfTI or FreeSurfer MGZ/MGH volume.

    The image is reoriented to nibabel's canonical orientation
    (approximately RAS+) before extracting the slices.
    """
    filename = Path(filename)

    if not filename.exists():
        raise FileNotFoundError(f"Volume not found: {filename}")

    image = nib.load(filename)
    image = nib.as_closest_canonical(image)

    volume = image.get_fdata()

    if volume.ndim != 3:
        raise ValueError(
            f"Expected a 3D volume, but got shape {volume.shape}"
        )

    return volume


def save_figure(fig, subject, output_filename):
    # Subject name as the overall title
    fig.suptitle(subject, fontsize=16)

    # Tight layout while leaving room for the title
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    output_filename = Path(output_filename)
    output_filename.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_filename,
        dpi=150,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Loading
    volume = load_volume(args.volume_filename)
    if args.overlay_filename is not None:
        overlay = load_volume(args.overlay_filename)
        if overlay.shape != volume.shape:
            raise ValueError(
                f"Overlay shape {overlay.shape} does not match "
                f"volume shape {volume.shape}"
            )
    else:
        overlay = None

    # Processing
    fig = create_screenshot(volume, overlay=overlay)

    # Saving
    save_figure(fig, args.subject, args.output_filename)


if __name__ == "__main__":
    main()
