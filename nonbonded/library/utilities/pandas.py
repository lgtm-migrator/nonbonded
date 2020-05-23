import numpy
import pandas


def reorder_data_frame(data_frame):
    """ Re-order the substance columns of a data frame so that the individual
    components are alphabetically sorted.

    Parameters
    ----------
    data_frame: pandas.DataFrame
        The data frame to re-order.

    Returns
    -------
    pandas.DataFrame
        The re-ordered data frame.
    """

    min_n_components = data_frame["N Components"].min()
    max_n_components = data_frame["N Components"].max()

    ordered_frames = []

    for n_components in range(min_n_components, max_n_components + 1):

        component_frame = data_frame[data_frame["N Components"] == n_components]
        ordered_frame = data_frame[data_frame["N Components"] == n_components].copy()

        component_headers = [f"Component {i + 1}" for i in range(n_components)]
        component_order = numpy.argsort(component_frame[component_headers], axis=1)

        substance_headers = ["Component", "Role", "Mole Fraction", "Exact Amount"]

        for component_index in range(n_components):

            indices = component_order[f"Component {component_index + 1}"]

            for substance_header in substance_headers:

                component_header = f"{substance_header} {component_index + 1}"

                if not component_header in ordered_frame:
                    continue

                for replacement_index in range(n_components):

                    if component_index == replacement_index:
                        continue

                    replacement_header = f"{substance_header} {replacement_index + 1}"

                    ordered_frame[component_header] = numpy.where(
                        indices == replacement_index,
                        component_frame[replacement_header],
                        component_frame[component_header],
                    )

        ordered_frames.append(ordered_frame)

    ordered_data_frame = pandas.concat(ordered_frames, ignore_index=True, sort=False)

    return ordered_data_frame