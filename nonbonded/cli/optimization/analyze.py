import logging
import os
from glob import glob

import click

from nonbonded.library.models.forcefield import ForceField
from nonbonded.library.models.projects import Optimization
from nonbonded.library.models.results import BenchmarkResult, OptimizationResult
from nonbonded.library.utilities.exceptions import ForceFieldNotFound
from nonbonded.library.utilities.logging import (
    get_log_levels,
    setup_timestamp_logging,
    string_to_log_level,
)

logger = logging.getLogger(__name__)


@click.command(help="Analyzes the output of an optimization.")
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(get_log_levels()),
    help="The verbosity of the server logger.",
    show_default=True,
)
def analyze(log_level):
    import numpy

    from forcebalance.nifty import lp_load

    from openff.evaluator.client import RequestResult
    from openff.evaluator.datasets import PhysicalPropertyDataSet

    from openforcefield.typing.engines.smirnoff import ForceField as OFFForceField

    # Set up logging if requested.
    logging_level = string_to_log_level(log_level)

    if logging_level is not None:
        setup_timestamp_logging(logging_level)

    # Load in the definition of the optimization to optimize.
    optimization = Optimization.parse_file("optimization.json")

    # Create a directory to store the results in
    output_directory = "analysis"
    os.makedirs(output_directory, exist_ok=True)

    # Load in the refit force field (if it exists)
    refit_force_field_path = os.path.join(
        "result", "optimize", optimization.initial_force_field
    )

    if not os.path.isfile(refit_force_field_path):

        raise ForceFieldNotFound(
            f"A refit force field could not be found (expected "
            f"path={refit_force_field_path}. Make sure that the optimization completed "
            f"at least one iteration successfully."
        )

    refit_force_field_off = OFFForceField(
        refit_force_field_path, allow_cosmetic_attributes=True
    )
    refit_force_field = ForceField(
        inner_xml=refit_force_field_off.to_string(discard_cosmetic_attributes=True)
    )

    # Load the reference data set
    reference_data_set = PhysicalPropertyDataSet.from_json(
        os.path.join(
            "targets", optimization.force_balance_input.target_name, "training-set.json"
        )
    )

    # Determine the number of optimization iterations.
    tmp_directory = os.path.join(
        "optimize.tmp", optimization.force_balance_input.target_name
    )

    n_iterations = len(glob(os.path.join(tmp_directory, "iter_*", "results.json")))

    if n_iterations == 0:

        raise ValueError(
            "No iteration results could be found, even though a refit force field "
            "was. Make sure not to delete the `optimize.tmp` directory after the "
            "optimization has completed."
        )

    # Analyse the results of each iteration.
    objective_function = []

    for iteration in range(n_iterations):

        logger.info(f"Analysing the results of iteration {iteration}")

        iteration_directory = os.path.join(
            tmp_directory, "iter_" + str(iteration).zfill(4)
        )
        iteration_results_path = os.path.join(iteration_directory, "results.json")

        if not os.path.isfile(iteration_results_path):
            logger.info(
                f"The results file could not be found for iteration {iteration}."
            )

            objective_function.append(numpy.nan)
            continue

        iteration_results = RequestResult.from_json(iteration_results_path)
        estimated_data_set = iteration_results.estimated_properties

        # Generate statistics about each iteration.
        analyzed_results = BenchmarkResult.from_evaluator(
            project_id=optimization.project_id,
            study_id=optimization.study_id,
            benchmark_id=optimization.id,
            reference_data_set=reference_data_set,
            estimated_data_set=estimated_data_set,
            analysis_environments=optimization.analysis_environments,
        )

        # Save the results
        with open(
            os.path.join(output_directory, f"iteration-{iteration}.json"), "w"
        ) as file:

            file.write(analyzed_results.json())

        # Extract the value of this iterations objective function
        objective_file_path = os.path.join(iteration_directory, "objective.p")
        objective_statistics = lp_load(objective_file_path)

        objective_function.append(objective_statistics["X"])

    # Save the full results
    optimization_results = OptimizationResult(
        project_id=optimization.project_id,
        study_id=optimization.study_id,
        id=optimization.id,
        objective_function=objective_function,
        refit_force_field=refit_force_field,
    )

    with open(os.path.join(output_directory, "optimization-results.json"), "w") as file:
        file.write(optimization_results.json())
