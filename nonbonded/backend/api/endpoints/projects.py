import os
from glob import glob

from fastapi import APIRouter, HTTPException

from nonbonded.library.models.datasets import SelectedDataSet
from nonbonded.library.models.project import Project
from nonbonded.library.models.results import EstimationResult

router = APIRouter()

PROJECT_DIRECTORY = os.path.join("rest", "projects")


@router.get("/")
async def get_projects():

    if not os.path.isdir(PROJECT_DIRECTORY):
        return {}

    project_paths = glob(os.path.join(PROJECT_DIRECTORY, "*/project.json"))

    projects = [Project.parse_file(project_path) for project_path in project_paths]

    return projects


@router.post("/")
async def post_project(project: Project):

    project_directory = os.path.join(PROJECT_DIRECTORY, project.identifier)
    os.makedirs(project_directory, exist_ok=True)

    project_path = os.path.join(project_directory, f"project.json")

    with open(project_path, "w") as file:
        file.write(project.json())

    return project


@router.get("/{project_id}")
async def get_project(project_id):

    project_directory = os.path.join(PROJECT_DIRECTORY, project_id)
    project_path = os.path.join(project_directory, f"project.json")

    if not os.path.isfile(project_path):
        raise HTTPException(status_code=404, detail="Item not found")

    project = Project.parse_file(project_path)

    return project


@router.get("/{project_id}/studies")
async def get_studies(project_id):

    project = await get_project(project_id)
    return project.studies


@router.get("/{project_id}/studies/{study_id}")
async def get_study(project_id, study_id):

    studies = await get_studies(project_id)

    if study_id not in studies:

        raise HTTPException(
            status_code=404,
            detail=f"Study {study_id} not found as part of project {project_id}",
        )

    return studies[study_id]


@router.get("/{project_id}/studies/{study_id}/test/dataset")
async def get_test_set(project_id, study_id):

    study_directory = os.path.join(PROJECT_DIRECTORY, project_id, study_id)
    study_path = os.path.join(study_directory, "dataset.json")

    if not os.path.isfile(study_path):
        raise HTTPException(status_code=404, detail="Study not found")

    data_set_summary = SelectedDataSet.parse_file(study_path)
    return data_set_summary


@router.post("/{project_id}/studies/{study_id}/test/dataset")
async def post_test_set(project_id, study_id, data_set_summary: SelectedDataSet):

    study_directory = os.path.join(PROJECT_DIRECTORY, project_id, study_id)
    os.makedirs(study_directory, exist_ok=True)

    study_path = os.path.join(study_directory, "dataset.json")

    with open(study_path, "w") as file:
        file.write(data_set_summary.json())

    return data_set_summary


@router.get("/{project_id}/studies/{study_id}/test/results")
async def get_test_results(project_id, study_id):

    study_directory = os.path.join(PROJECT_DIRECTORY, project_id, study_id)
    results_path = os.path.join(study_directory, "test_results.json")

    if not os.path.isfile(results_path):
        raise HTTPException(status_code=404, detail="Study test results not found.")

    benchmark_results = EstimationResult.parse_file(results_path)
    return benchmark_results


@router.post("/{project_id}/studies/{study_id}/test/results")
async def post_test_results(project_id, study_id, results: EstimationResult):

    study_directory = os.path.join(PROJECT_DIRECTORY, project_id, study_id)
    os.makedirs(study_directory, exist_ok=True)

    results_path = os.path.join(study_directory, "test_results.json")

    with open(results_path, "w") as file:
        file.write(results.json())

    return results


@router.get("/{project_id}/studies/{study_id}/train")
async def get_optimizations(project_id, study_id):

    study = await get_study(project_id, study_id)
    return {x.identifier: x for x in study.optimizations}


@router.get("/{project_id}/studies/{study_id}/train/{optimization_id}")
async def get_optimization(project_id, study_id, optimization_id):

    optimizations = await get_optimizations(project_id, study_id)

    if optimization_id not in optimizations:

        raise HTTPException(
            status_code=404,
            detail=f"Optimization {optimization_id} not found as part of study "
            f"{project_id} and project {project_id}",
        )

    return optimizations[optimization_id]


@router.get("/{project_id}/studies/{study_id}/train/{optimization_id}/dataset")
async def get_train_set(project_id, study_id, optimization_id):

    optimization_directory = os.path.join(
        PROJECT_DIRECTORY, project_id, study_id, optimization_id
    )
    optimization_path = os.path.join(optimization_directory, f"dataset.json")

    if not os.path.isfile(optimization_path):
        raise HTTPException(status_code=404, detail="Optimization data set not found.")

    data_set_summary = SelectedDataSet.parse_file(optimization_path)

    return data_set_summary


@router.post("/{project_id}/studies/{study_id}/train/{optimization_id}/dataset")
async def post_train_set(
    project_id, study_id, optimization_id, data_set_summary: SelectedDataSet
):

    optimization_directory = os.path.join(
        PROJECT_DIRECTORY, project_id, study_id, optimization_id
    )
    os.makedirs(optimization_directory, exist_ok=True)

    optimization_path = os.path.join(optimization_directory, f"dataset.json")

    with open(optimization_path, "w") as file:
        file.write(data_set_summary.json())

    return data_set_summary