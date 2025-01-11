import traceback 

from pydantic import BaseModel, Field
from typing import Annotated, Literal, List, Optional, Type

from langchain_core.tools import tool

class TimeSeriesTimeDataPoint(BaseModel):
    year: int
    month: int
    day: int

class TimeSeriesDataPoint(BaseModel):
    time: TimeSeriesTimeDataPoint = Field("The time of the data point")
    value: float

class TimeSeries(BaseModel):
    name: str = Field("The name of the series (provide data units (e.g. $ million) in brackets )")
    data: List[TimeSeriesDataPoint]

class TimeSeriesPlot(BaseModel):
    series: List[TimeSeries]

@tool 
async def time_series_plotter(
    time_series_input_data: Annotated[TimeSeriesPlot, "Time series"],
):
    """Use this to plot a time series for the user. Returns time series json data if successful."""
    return str({"time_series": time_series_input_data.model_dump()})

class TreeMapDataPoint(BaseModel):
    x: str = Field("The label for the data point")
    y: float

class TreeMapSeries(BaseModel):
    name: str = Field("The name of the series (provide data units (e.g. $ million) in brackets )")
    data: List[TreeMapDataPoint]

class MultiDimentionalTreemapInputData(BaseModel):
    series: List[TreeMapSeries]

@tool 
async def basic_treemap_plotter(
    treemap_input_data: Annotated[TreeMapSeries, "Treemap series"],
):
    """Use this to plot the basic treemap for the user. Returns treemap json data if successful."""
    return str({"basic_treemap": treemap_input_data.model_dump()})


@tool 
async def multi_dimentional_treemap_plotter(
    treemap_input_data: Annotated[MultiDimentionalTreemapInputData, "Multi-dimentional treemap series"],
):
    """Use this to plot a multi-dimensional treemap for the user. Returns treemap json data if successful."""
    return str({"multi_dimentional_treemap": treemap_input_data.model_dump()})


class Node(BaseModel):
    id: str = Field("Node ID")
    title: str = Field("human-readable name or title of the node")

class Edge(BaseModel):
    source: str = Field("the ID of the source node")
    target: str = Field("the ID of the target node")
    value: float = Field("the weight of the edge (e.g., the strength of the relationship)")

class SankeyChart(BaseModel):
    nodes: List[Node] = Field("list of Node objects, each representing a node in the graph")
    edges: List[Edge] = Field("list of Edge objects, each representing an edge in the graph")

@tool 
async def sankey_chart_plotter(
    sankey_chart_input_data: Annotated[SankeyChart, "Sankey chart data"],
):
    """Use this to plot a sankey chart for the user. Returns sankey chart json data if successful."""
    return str({"sankey_chart": sankey_chart_input_data.model_dump()})

plotter_tools = [
    time_series_plotter,
    basic_treemap_plotter,
    multi_dimentional_treemap_plotter,
    # sankey_chart_plotter
]

plotter_toolnames = [tool.name for tool in plotter_tools]

if __name__ == "__main__":
    print(plotter_toolnames)