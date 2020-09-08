import logging
from typing import List, TypeVar

from nonbonded.library.factories.factories import BaseRecursiveFactory
from nonbonded.library.factories.inputs.evaluator import (
    ComputeResources,
    DaskHPCClusterConfig,
    DaskLocalClusterConfig,
    EvaluatorServerConfig,
    QueueWorkerResources,
)
from nonbonded.library.models.projects import Benchmark, Optimization, Project, Study
from nonbonded.library.templates.submission import Submission, SubmissionTemplate

logger = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S")


class InputFactory(BaseRecursiveFactory):
    """A factory used to create the directory structure and inputs for a particular
    model (project, study, optimization or benchmark).
    """

    @classmethod
    def model_type_to_factory(cls, model_type):

        from nonbonded.library.factories.inputs.benchmark import BenchmarkFactory
        from nonbonded.library.factories.inputs.optimization import OptimizationFactory

        if issubclass(model_type, (Project, Study)):
            return InputFactory
        elif issubclass(model_type, Optimization):
            return OptimizationFactory
        elif issubclass(model_type, Benchmark):
            return BenchmarkFactory

        raise NotImplementedError()

    @classmethod
    def _generate_evaluator_config(
        cls, preset_name: str, conda_environment: str, n_workers: int, port: int
    ) -> EvaluatorServerConfig:
        """Generates an Evaluator server configuration."""

        if preset_name == "lilac-local":

            backend_config = DaskLocalClusterConfig(
                resources_per_worker=ComputeResources()
            )

        elif preset_name == "lilac-dask":

            # noinspection PyTypeChecker
            backend_config = DaskHPCClusterConfig(
                maximum_workers=n_workers,
                resources_per_worker=QueueWorkerResources(),
                queue_name="gpuqueue",
                setup_script_commands=[
                    f"conda activate {conda_environment}",
                    "module load cuda/10.1",
                ],
            )

        else:
            raise NotImplementedError()

        server_config = EvaluatorServerConfig(backend_config=backend_config, port=port)

        return server_config

    @classmethod
    def _generate_submission_script(
        cls,
        job_name: str,
        conda_environment: str,
        evaluator_preset: str,
        max_time: str,
        commands: List[str],
    ):
        """Generates an LSF bash submission script.

        Parameters
        ----------
        job_name
            The name of the LSF job.
        conda_environment
            The name of the conda environment to run within.
        max_time
            The maximum wall-clock time for job submissions.
        evaluator_preset
            The present evaluator compute settings to use.
        commands
            The commands to run in the script.
        """

        submission = Submission(
            job_name=job_name,
            wall_clock_limit=max_time,
            max_memory=8,
            gpu=evaluator_preset == "lilac-local",
            environment_name=conda_environment,
            commands=commands,
        )
        with open("submit.sh", "w") as file:
            file.write(SubmissionTemplate.generate("submit_lilac.txt", submission))

    @classmethod
    def _generate(cls, **kwargs):

        with open("README.md", "w") as file:
            file.write(kwargs["model"].description)

    @classmethod
    def generate(
        cls,
        model: T,
        conda_environment: str,
        max_time: str,
        evaluator_preset: str,
        evaluator_port: int,
        n_evaluator_workers: int,
        include_results: bool,
    ):
        """Generates the required directory structure and inputs for the model.

        Parameters
        ----------
        model
            The model to generate the inputs for.
        conda_environment
            The name of the conda environment to run within.
        max_time
            The maximum wall-clock time for job submissions.
        evaluator_preset
            The present evaluator compute settings to use.
        evaluator_port
            The port to run the evaluator server on.
        n_evaluator_workers
            The target number of evaluator compute workers to spawn.
        include_results
            Whether to also download any previously generated results
            and store them alongside the inputs.
        """

        super(InputFactory, cls).generate(
            model=model,
            conda_environment=conda_environment,
            max_time=max_time,
            evaluator_preset=evaluator_preset,
            evaluator_port=evaluator_port,
            n_evaluator_workers=n_evaluator_workers,
            include_results=include_results,
        )
