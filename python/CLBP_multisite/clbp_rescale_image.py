#!/usr/bin/env python3

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np


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

    volume = image.get_fdata()

    if volume.ndim != 3:
        raise ValueError(
            f"Expected a 3D volume, but got shape {volume.shape}"
        )

    return image, volume


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",
                        help="Input 3D volume.")
    parser.add_argument("output",
                        help="Output 3D volume.")
    parser.add_argument("min", type=int,
                        help="Min of new range.")
    parser.add_argument("max", type=int,
                        help="Max of new range.")

    args = parser.parse_args()

    img, data = load_volume(args.input)

    # Your intensity transformation here
    # Rescale values to [0, 1]
    data = data - np.min(data)
    data = data / np.max(data)

    data = data * (args.max - args.min) + args.min

    output = nib.Nifti1Image(data, img.affine, img.header)
    nib.save(output, args.output)



if __name__ == "__main__":
    main()
