import traceback 

from pydantic import BaseModel, Field
from typing import Annotated, Literal, List, Optional, Type, Union

from langchain_core.tools import tool

# Stock price plot
class StockPricePlotData(BaseModel):
    ticker: Annotated[str, "Company ticker"]

# Time series plot models
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

class TimeSeriesPlotData(BaseModel):
    series: List[TimeSeries]

# Treemap plot models
class TreeMapDataPoint(BaseModel):
    x: str = Field("The label for the data point")
    y: float

class TreeMapSeries(BaseModel):
    name: str = Field("The name of the series (provide data units (e.g. $ million) in brackets )")
    data: List[TreeMapDataPoint]

class TreemapPlotData(BaseModel):
    series: List[TreeMapSeries]

# Sankey chart models
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

# Master model
class PlotterOutputModel(BaseModel):
    widget_id: str
    plot_type: Literal["time_series", "treemap", "stock_price", "None"]
    plot_data: Optional[Union[
        TimeSeriesPlotData,TreemapPlotData, StockPricePlotData, Literal["None"]
        ]] = Field("Selected plot type data or None if not plotting")
    reason: Optional[str]

