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


def save_screenshot(subject, volume_filename,
                    output_filename, overlay_filename=None):
    volume = load_volume(volume_filename)

    if overlay_filename is not None:
        overlay = load_volume(overlay_filename)

        if overlay.shape != volume.shape:
            raise ValueError(
                f"Overlay shape {overlay.shape} does not match "
                f"volume shape {volume.shape}"
            )

        overlay = overlay > 0

    # Middle voxel in each dimension
    middle_x = volume.shape[0] // 2
    middle_y = volume.shape[1] // 2
    middle_z = volume.shape[2] // 2

    # Two sagittal slices: middle - 10 and middle + 10
    sagittal_minus = middle_x - 10
    sagittal_plus = middle_x + 10

    if sagittal_minus < 0 or sagittal_plus >= volume.shape[0]:
        raise ValueError(
            f"Volume is too small for sagittal slices at "
            f"middle +/- 10. Shape: {volume.shape}"
        )

    # Extract slices.
    #
    # After as_closest_canonical(), axes are approximately:
    #   X = left/right
    #   Y = posterior/anterior
    #   Z = inferior/superior
    #
    # Transposing makes the displayed images have the expected
    # horizontal/vertical orientation.
    coronal = volume[:, middle_y, :].T
    axial = volume[:, :, middle_z].T
    sagittal_minus_image = volume[sagittal_minus, :, :].T
    sagittal_plus_image = volume[sagittal_plus, :, :].T

    if overlay_filename is not None:
        coronal_overlay = overlay[:, middle_y, :].T
        axial_overlay = overlay[:, :, middle_z].T
        sagittal_minus_overlay = overlay[sagittal_minus, :, :].T
        sagittal_plus_overlay = overlay[sagittal_plus, :, :].T

    fig, axes = plt.subplots(2, 2,
                             figsize=(10, 10),
                             facecolor="white")

    # Coronal
    axes[0, 0].imshow(coronal, cmap="gray",
                      origin="lower")
    if overlay_filename is not None:
        axes[0, 0].contour(coronal_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[0, 0].set_title("Coronal")

    # Axial
    axes[0, 1].imshow(axial, cmap="gray",
                      origin="lower")
    if overlay_filename is not None:
        axes[0, 1].contour(axial_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[0, 1].set_title("Axial")

    # Sagittal - 10
    axes[1, 0].imshow(sagittal_minus_image,
                      cmap="gray", origin="lower")
    if overlay_filename is not None:
        axes[1, 0].contour(sagittal_minus_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[1, 0].set_title(f"Sagittal ({middle_x - 10})")

    # Sagittal + 10
    axes[1, 1].imshow(sagittal_plus_image,
                      cmap="gray", origin="lower")
    if overlay_filename is not None:
        axes[1, 1].contour(sagittal_plus_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[1, 1].set_title(f"Sagittal ({middle_x + 10})")

    # Remove axes/ticks
    for ax in axes.flat:
        ax.axis("off")

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
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("subject",
                        help="Subject name to display as the figure title.")
    parser.add_argument("volume",
                        help="Input 3D volume (.nii, .nii.gz, .mgz, or .mgh).")
    parser.add_argument("output", help="Output PNG filename.")
    parser.add_argument("--overlay",
                        help="Optional binary mask to display as a contour.")

    args = parser.parse_args()

    save_screenshot(
        subject=args.subject,
        volume_filename=args.volume,
        output_filename=args.output,
        overlay_filename=args.overlay,
    )


if __name__ == "__main__":
    main()