import click

from nonbonded.library.models.projects import Benchmark
from nonbonded.library.utilities.logging import (
    get_log_levels,
    setup_timestamp_logging,
    string_to_log_level,
)


@click.command(help="Retrieve a benchmark from the REST API.")
@click.option(
    "--project-id", type=click.STRING, help="The id of the parent project.",
)
@click.option(
    "--study-id", type=click.STRING, help="The id of the parent study.",
)
@click.option(
    "--benchmark-id", type=click.STRING, help="The id of the benchmark to retrieve.",
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(get_log_levels()),
    help="The verbosity of the logger.",
    show_default=True,
)
def retrieve(project_id, study_id, benchmark_id, log_level):

    # Set up logging if requested.
    logging_level = string_to_log_level(log_level)

    if logging_level is not None:
        setup_timestamp_logging(logging_level)

    benchmark = Benchmark.from_rest(
        project_id=project_id, study_id=study_id, benchmark_id=benchmark_id
    )
    benchmark_json = benchmark.json()

    print(benchmark_json)
