from textwrap import TextWrapper

import click

from nonbonded.library.models.projects import Study


@click.command(
    name="list",
    help="Lists the optimizations of a particular study."
)
@click.option(
    "--project-id", type=click.STRING, help="The id of the parent project.",
)
@click.option(
    "--study-id", type=click.STRING, help="The id of the study.",
)
def list_optimizations(project_id: str, study_id: str):

    study = Study.from_rest(project_id=project_id, study_id=study_id)

    print(f"Listing the optimizations of study={study_id} (project={project_id}):\n")

    text_wrapper = TextWrapper(initial_indent="    ", subsequent_indent="    ")

    for index, optimization in enumerate(study.optimizations):

        print(f"{index}) {optimization.id}\n")
        print("\n".join(text_wrapper.wrap(optimization.name)))
        print()
        print("\n".join(text_wrapper.wrap(optimization.description.split("\n")[0])))
        print()
