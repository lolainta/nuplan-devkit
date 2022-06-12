from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from nuplan.planning.metrics.metric_dataframe import MetricStatisticsDataFrame


class MetricStatisticsType(Enum):
    """Enum of different types for statistics."""

    MAX: str = 'MAX'
    MIN: str = 'MIN'
    P90: str = 'P90'
    MEAN: str = 'MEAN'
    COUNT: str = 'COUNT'
    VALUE: str = 'VALUE'
    DISTANCE: str = 'DISTANCE'
    VELOCITY: str = 'VELOCITY'
    BOOLEAN: str = 'BOOLEAN'
    RATIO: str = 'RATIO'

    def __str__(self) -> str:
        """Metric type string representation."""
        return str(self.value)

    def __repr__(self) -> str:
        """Metric type string representation."""
        return str(self.value)

    def serialize(self) -> str:
        """Serialize the type when saving."""
        return self.value

    @classmethod
    def deserialize(cls, key: str) -> MetricStatisticsType:
        """Deserialize the type when loading from a string."""
        return MetricStatisticsType.__members__[key]


@dataclass
class MetricResult(ABC):
    """
    Abstract MetricResult.
    """

    metric_computator: str  # Name of metric computator
    name: str  # Name of the metric
    metric_category: str  # Category of metric

    def serialize(self) -> Dict[str, Any]:
        """Serialize the metric result."""
        pass

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> MetricResult:
        """
        Deserialize the metric result when loading from a file.
        :param data; A dictionary of data in loading.
        """
        pass

    def serialize_dataframe(self) -> Dict[str, Any]:
        """
        Serialize a dictionary for dataframe.
        :return a dictionary
        """
        pass


@dataclass
class Statistic:
    """
    Class to report statsitcs of metrics.
    """

    name: str  # name of statistic
    unit: str  # unit of statistic
    value: Union[float, bool]  # value of the statistic

    def serialize(self) -> Dict[str, Any]:
        """Serialization of TimeSeries."""
        return {'name': self.name, 'unit': self.unit, 'value': self.value}

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Statistic:
        """
        Deserialization of TimeSeries
        :param data: A dictionary of data
        :return A Statistic data class.
        """
        return Statistic(name=data['name'], unit=data['unit'], value=data['value'])


@dataclass
class TimeSeries:
    """
    Class to report time series data of metrics.
    """

    unit: str  # unit of the time series
    time_stamps: List[int]  # time stamps of the time series [microseconds]
    values: List[float]  # values of the time series

    def __post_init__(self) -> None:
        """Post initialization of TimeSeries."""
        assert len(self.time_stamps) == len(self.values)

    def serialize(self) -> Dict[str, Any]:
        """Serialization of TimeSeries."""
        return {'unit': self.unit, 'time_stamps': self.time_stamps, 'values': self.values}

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> Optional[TimeSeries]:
        """
        Deserialization of TimeSeries
        :param data: A dictionary of data
        :return A TimeSeries dataclass.
        """
        return (
            TimeSeries(unit=data['unit'], time_stamps=data['time_stamps'], values=data['values'])
            if data is not None
            else None
        )


@dataclass
class MetricStatistics(MetricResult):
    """Class to report results of metric statistics."""

    statistics: Dict[MetricStatisticsType, Statistic]  # Collection of statistics
    time_series: Optional[TimeSeries]  # time series data of the metric
    metric_score: Optional[float] = None  # Final score of a metric in a scenario

    def serialize(self) -> Dict[str, Any]:
        """Serialize the metric result."""
        return {
            'metric_computator': self.metric_computator,
            'name': self.name,
            'statistics': {
                statistic_type.serialize(): statistics.serialize()
                for statistic_type, statistics in self.statistics.items()
            },
            'time_series': self.time_series.serialize() if self.time_series is not None else None,
            'metric_category': self.metric_category,
            'metric_score': self.metric_score,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> MetricStatistics:
        """
        Deserialize the metric result when loading from a file.
        :param data; A dictionary of data in loading.
        """
        return MetricStatistics(
            metric_computator=data['metric_computator'],
            name=data['name'],
            statistics={
                MetricStatisticsType.deserialize(statistic_type): Statistic.deserialize(statistics)
                for statistic_type, statistics in data['statistics'].items()
            },
            time_series=TimeSeries.deserialize(data['time_series']),
            metric_category=data['metric_category'],
            metric_score=data['metric_score'],
        )

    def serialize_dataframe(self) -> Dict[str, Any]:
        """
        Serialize a dictionary for dataframe
        :return a dictionary
        """
        columns: Dict[str, Any] = {'metric_score': self.metric_score, 'metric_category': self.metric_category}
        for statistic_type, statistic in self.statistics.items():
            statistic_columns = {
                f'{statistic.name}_stat_type': statistic_type.serialize(),
                f'{statistic.name}_stat_unit': [statistic.unit],
                f'{statistic.name}_stat_value': [statistic.value],
            }
            columns.update(statistic_columns)

        if self.time_series is None:
            time_series_unit_column = [None]
            time_series_timestamp_column = [None]
            time_series_values_column = [None]
        else:
            time_series_unit_column = [self.time_series.unit]  # type: ignore
            time_series_timestamp_column = [[int(timestamp) for timestamp in self.time_series.time_stamps]]  # type: ignore
            time_series_values_column = [self.time_series.values]  # type: ignore

        time_series_columns = {
            MetricStatisticsDataFrame.time_series_unit_column: time_series_unit_column,
            MetricStatisticsDataFrame.time_series_timestamp_column: time_series_timestamp_column,
            MetricStatisticsDataFrame.time_series_values_column: time_series_values_column,
        }
        columns.update(time_series_columns)
        return columns


@dataclass
class MetricViolation(MetricResult):
    """Class to report results of violation-based metrics."""

    unit: str  # unit of the violation
    start_timestamp: int  # start time stamp of the violation [microseconds]
    duration: int  # duration of the violation [microseconds]
    extremum: float  # the most violating value of the violation
    mean: float  # The average violation level

    def serialize(self) -> Dict[str, Any]:
        """Serialize the metric result."""
        return {
            'metric_computator': self.metric_computator,
            'name': self.name,
            'unit': self.unit,
            'start_timestamp': self.start_timestamp,
            'duration': self.duration,
            'extremum': self.extremum,
            'metric_category': self.metric_category,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> MetricViolation:
        """
        Deserialize the metric result when loading from a file
        :param data; A dictionary of data in loading.
        """
        return MetricViolation(
            metric_computator=data['metric_computator'],
            name=data['name'],
            start_timestamp=data['start_timestamp'],
            duration=data['duration'],
            extremum=data['extremum'],
            unit=data['unit'],
            metric_category=data['metric_category'],
            mean=data['mean'],
        )
