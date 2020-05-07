from typing import Dict, List, Tuple

from pydantic import BaseModel, Field


class ScatterSeries(BaseModel):

    name: str = Field(..., description="The name of this series.")

    x: List[float] = Field(..., description="The x values of the series.")
    y: List[float] = Field(..., description="The y values of the series.")

    metadata: List[str] = Field(
        ...,
        description="String metadata (e.g. smiles) associated with each " "data point.",
    )


class ScatterData(BaseModel):

    title: str = Field(..., description="The title of this data set.")

    series: List[ScatterSeries] = Field(
        ..., description="The different series of this set."
    )


class StatisticSeries(BaseModel):

    name: str = Field(..., description="The name of this series.")

    value: Dict[str, float] = Field(
        ..., description="The value of this series statistic."
    )
    confidence_intervals: Dict[str, Tuple[float, float]] = Field(
        ..., description="The 95% confidence intervals."
    )


class StatisticData(BaseModel):

    title: str = Field(..., description="The title of this data set.")

    series: StatisticSeries = Field(..., description="The series of this set.")


class PropertyResults(BaseModel):

    scatter_data: Dict[str, ScatterData] = Field(
        ...,
        description="The estimated vs reference obtained for each force field "
        "that was benchmarked against.",
    )

    statistic_data: Dict[str, StatisticData] = Field(
        ..., description="Bootstrapped-statistics about the data."
    )


class EstimationResult(BaseModel):

    property_results: Dict[str, PropertyResults] = Field(
        ...,
        description="The estimated vs reference results for each class of property.",
    )
    conda_environment_id: str = Field(
        ...,
        description="The unique id of the conda environment used during the estimation.",
    )


class OptimizationResult(BaseModel):

    objective_function: ScatterSeries = Field(
        ..., description="The value of the objective function"
    )
    conda_environment_id: str = Field(
        ...,
        description="The unique id of the conda environment used during the "
        "optimization.",
    )