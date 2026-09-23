#!/usr/bin/env python3

import matplotlib.pyplot as plt


def create_screenshot(volume, overlay=None):
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

    if overlay is not None:
        overlay = overlay > 0
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
    if overlay is not None:
        axes[0, 0].contour(coronal_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[0, 0].set_title("Coronal")

    # Axial
    axes[0, 1].imshow(axial, cmap="gray",
                      origin="lower")
    if overlay is not None:
        axes[0, 1].contour(axial_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[0, 1].set_title("Axial")

    # Sagittal - 10
    axes[1, 0].imshow(sagittal_minus_image,
                      cmap="gray", origin="lower")
    if overlay is not None:
        axes[1, 0].contour(sagittal_minus_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[1, 0].set_title(f"Sagittal ({middle_x - 10})")

    # Sagittal + 10
    axes[1, 1].imshow(sagittal_plus_image,
                      cmap="gray", origin="lower")
    if overlay is not None:
        axes[1, 1].contour(sagittal_plus_overlay,
                           levels=[0.5],
                           colors="blue",
                           linewidths=1.5)
    axes[1, 1].set_title(f"Sagittal ({middle_x + 10})")

    # Remove axes/ticks
    for ax in axes.flat:
        ax.axis("off")

    return fig
