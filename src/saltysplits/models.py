from __future__ import annotations
from pandas import Timedelta
from pydantic import conint
from pydantic_xml import BaseXmlModel, attr, element, wrapped
from typing import List, Optional
from saltysplits.annotations import TimeOptional, DateTime, SBool, OffsetOptional, LssVersion


class Splits(BaseXmlModel, tag="Run", arbitrary_types_allowed=True, search_mode="ordered"):
    version: LssVersion = attr(name="version")
    game_icon: Optional[str] = element(tag="GameIcon", default=None)
    game_name: str = element(tag="GameName")
    category_name: str = element(tag="CategoryName")
    layout_path: Optional[str] = element(tag="LayoutPath", default=None)
    offset: OffsetOptional = element(tag="Offset", default=Timedelta(0))
    attempt_count: Optional[conint(ge=0)] = element(tag="AttemptCount", default=0)
    attempt_history: Optional[List[Attempt]] = wrapped("AttemptHistory", default=None)
    segments: List[Segment] = wrapped("Segments")


class BaseTime(BaseXmlModel, arbitrary_types_allowed=True, search_mode="ordered"):
    real_time: TimeOptional = element(tag="RealTime", default=None)
    game_time: TimeOptional = element(tag="GameTime", default=None)


class Attempt(BaseTime, tag="Attempt"):
    id: str = attr(name="id")
    started: Optional[DateTime] = attr(name="started", default=None)
    is_started_synced: Optional[SBool] = attr(name="isStartedSynced", default=None)
    ended: Optional[DateTime] = attr(name="ended", default=None)
    is_ended_synced: Optional[SBool] = attr(name="isEndedSynced", default=None)


class Segment(BaseXmlModel, tag="Segment", arbitrary_types_allowed=True, search_mode="ordered"):
    name: str = element(tag="Name")
    icon: Optional[str] = element(tag="Icon", default=None)
    split_times: List[SplitTime] = wrapped("SplitTimes")
    best_segment_time: BaseTime = element(tag="BestSegmentTime")
    segment_history: Optional[List[Time]] = wrapped("SegmentHistory", default=None)


class SplitTime(BaseTime, tag="SplitTime"):
    name: str = attr(name="name")


class Time(BaseTime, tag="Time"):
    id: str = attr(name="id")


# ensures all model elements are defined when we need them (without relying on arbritrary definition order)
Splits.model_rebuild()
Segment.model_rebuild()
