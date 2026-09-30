#!/usr/bin/env python3

"""
Create a comparison screenshot of two 3D NIfTI or MGZ volumes.
The figure contains coronal, axial, and two sagittal views,
with volume 1 on the left and volume 2 on the right.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import nibabel as nib

# Blue -> black -> red
heatmap = LinearSegmentedColormap.from_list(
    "diff_map",
    ["blue", "black", "red"]
)


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


def save_screenshot(subject, volume1,
                    volume2, output_filename):
    if volume1.shape != volume2.shape:
        raise ValueError(
            f"Volumes must have the same shape. "
            f"Volume 1: {volume1.shape}, "
            f"Volume 2: {volume2.shape}"
        )

    # =======
    # 1) Get the slices
    # =======

    # Middle voxel in each dimension
    middle_x = volume1.shape[0] // 2
    middle_y = volume1.shape[1] // 2
    middle_z = volume1.shape[2] // 2

    # Two sagittal slices: middle - 10 and middle + 10
    sagittal_minus = middle_x - 10
    sagittal_plus = middle_x + 10

    if sagittal_minus < 0 or sagittal_plus >= volume1.shape[0]:
        raise ValueError(
            f"Volume is too small for sagittal slices at "
            f"middle +/- 10. Shape: {volume1.shape}"
        )

    # Extract slices from volume 1.
    coronal1 = volume1[:, middle_y, :].T
    axial1 = volume1[:, :, middle_z].T
    sagittal_minus1 = volume1[sagittal_minus, :, :].T
    sagittal_plus1 = volume1[sagittal_plus, :, :].T

    # Extract slices from volume 2.
    coronal2 = volume2[:, middle_y, :].T
    axial2 = volume2[:, :, middle_z].T
    sagittal_minus2 = volume2[sagittal_minus, :, :].T
    sagittal_plus2 = volume2[sagittal_plus, :, :].T

    # ==========
    # 2) Prepare the figure
    # ==========
    print("Preparing the figure")
    vmin = min(volume1.min(), volume2.min())
    vmax = max(volume1.max(), volume2.max())

    fig, axes = plt.subplots(2, 5,
                             figsize=(25, 10),
                             facecolor="white")

    # LEFT SIDE = volume 1

    # Coronal
    axes[0, 0].imshow(coronal1, cmap="gray",
                      origin="lower", vmin=vmin, vmax=vmax)
    axes[0, 0].set_title("Volume 1 - Coronal")

    # Axial
    axes[0, 1].imshow(axial1, cmap="gray",
                      origin="lower", vmin=vmin, vmax=vmax)
    axes[0, 1].set_title("Volume 1 - Axial")

    # Sagittal - 10
    axes[1, 0].imshow(sagittal_minus1,
                      cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
    axes[1, 0].set_title(
        f"Volume 1 - Sagittal ({sagittal_minus})")

    # Sagittal + 10
    axes[1, 1].imshow(sagittal_plus1,
                      cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
    axes[1, 1].set_title(
        f"Volume 1 - Sagittal ({sagittal_plus})")


    # RIGHT SIDE = VOLUME 2
    axes[0, 2].imshow(coronal2, cmap="gray",
                      origin="lower", vmin=vmin, vmax=vmax)
    axes[0, 2].set_title("Volume 2 - Coronal")

    axes[0, 3].imshow(axial2, cmap="gray",
                      origin="lower", vmin=vmin, vmax=vmax)
    axes[0, 3].set_title("Volume 2 - Axial")

    axes[1, 2].imshow(sagittal_minus2,
                      cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
    axes[1, 2].set_title(
        f"Volume 2 - Sagittal ({sagittal_minus})"
    )

    axes[1, 3].imshow(sagittal_plus2,
                      cmap="gray", origin="lower", vmin=vmin, vmax=vmax)
    axes[1, 3].set_title(
        f"Volume 2 - Sagittal ({sagittal_plus})"
    )

    # DIFFERENCE
    diff = volume2 - volume1
    max_abs = max(abs(diff.min()), abs(diff.max()))
    vmin = -max_abs
    vmax = max_abs

    axes[0, 4].imshow(axial2 - axial1, cmap=heatmap,
                      origin="lower", vmin=vmin, vmax=vmax)
    axes[0, 4].set_title("Difference - axial")

    axes[1, 4].imshow(sagittal_minus2 - sagittal_minus1,
                      cmap=heatmap, origin="lower", vmin=vmin, vmax=vmax)
    axes[1, 4].set_title(
        f"Difference - Sagittal ({sagittal_minus})"
    )

    # Remove axes/ticks
    for ax in axes.flat:
        ax.axis("off")

    # Subject name as the overall title
    fig.suptitle(subject, fontsize=16)

    # Tight layout while leaving room for the title
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    output_filename = Path(output_filename)
    output_filename.parent.mkdir(parents=True, exist_ok=True)


    # Add vertical lines
    fig.add_artist(
        plt.Line2D([0.4, 0.4], [0, 1],
                   transform=fig.transFigure,
                   color="black",
                   linewidth=2)
    )
    fig.add_artist(
        plt.Line2D([0.8, 0.8], [0, 1],
                   transform=fig.transFigure,
                   color="black",
                   linewidth=2)
    )

    print("Saving the figure")
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
    parser.add_argument("volume1",
                        help="First input 3D volume.")
    parser.add_argument("volume2",
                        help="Second input 3D volume.")
    parser.add_argument("output",
                        help="Output PNG filename.")

    args = parser.parse_args()

    print("Loading volumes...")
    volume1 = load_volume(args.volume1)
    volume2 = load_volume(args.volume2)

    save_screenshot(
        subject=args.subject,
        volume1=volume1,
        volume2=volume2,
        output_filename=args.output,
    )


if __name__ == "__main__":
    main()
