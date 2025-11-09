from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional
from saltysplits.enums import TimeType
from saltysplits.annotations import encode_time
from saltysplits.models import Splits


class SaltySplits(Splits):
    """
    Main interface for deserializing LiveSplit files (LSS) and interacting with the speedrunning data within.

    Args:
        Splits (Splits): Root pydantic-xml model, parent to all other LSS elements and attributes

    Returns:
        SaltySplits: Instanced pydantic-xml model containing deserialized speedrunning data and formatting functionality
    """

    @classmethod
    def read_lss(cls, lss_path: Path) -> SaltySplits:
        """
        Reads a LiveSplit file (LSS) as a SaltySplits root model instance (and populate it with validated splits, runs, attempts and segments).

        Args:
            lss_path (Path): Path to the LiveSplit file (.LSS)

        Returns:
            SaltySplits: Instanced pydantic-xml model containing deserialized speedrunning data and formatting functionality
        """

        with open(lss_path, "rb") as file:
            xml_bytes = file.read()
        return cls.from_xml(xml_bytes)

    def _collect_ids(self) -> List[Optional[str]]:
        """
        Iterates over all splits and attempts to find all unique run IDs (including those from deleted or otherwise partial runs)

        Returns:
            List[Optional[str]]: A list of unique run IDs (sorted as integers if possible)
        """

        run_ids = set()
        run_ids.update([attempt.id for attempt in self.attempt_history])
        run_ids.update([split.id for segment in self.segments if segment.segment_history for split in segment.segment_history])  # fmt: skip
        run_ids = list(run_ids)

        # sort them as int if possible
        if all(map(lambda x: str(int(x)) == x, run_ids)):
            run_ids = sorted(run_ids, key=lambda x: int(x))
        return run_ids

    def is_comparable(self, other: SaltySplits, strict: bool = True) -> bool:
        """
        Determines whether two SaltySplits instances pertain to the same topic.
        This is done by comparing their GameName / CategoryName values and the number of
        segments (and their exact Segment.Name values if strict is set)

        Args:
            other (SaltySplits): Another SaltySplits instance to compare against
            strict (bool, optional): Whether segment names need to match. Defaults to True.

        Returns:
            bool: True if runs from given instances can be compared, False if not
        """

        same_game = self.game_name == other.game_name
        same_category = self.category_name == other.category_name
        same_count = len(self.segments) == len(other.segments)
        same_segments = all([self.segments[i].name == other.segments[i].name for i in range(len(self.segments))]) if same_count and strict else not strict  # fmt: skip
        return all([same_game, same_category, same_count, same_segments])

    def to_df(
        self,
        time_type: TimeType = TimeType.REAL_TIME,
        allow_partial: bool = False,
        allow_empty: bool = False,
        cumulative: bool = False,
        lss_repr: bool = False,
        lss_ns: bool = True,
    ) -> pd.DataFrame:
        """
        Iterates over all splits to reconstruct individual runs (partial or otherwise) and represent them as a single pandas.DataFrame.
        Can then be used for further analysis within Python or dumped to common formats for use outside (e.g. see pandas.DataFrame.to_csv)

        Args:
            time_type (TimeType, optional): Whether to use GameTime or RealTime values. Defaults to REAL_TIME.
            allow_partial (bool, optional): Whether to allow runs that don't have values for all segments. Defaults to False.
            allow_empty (bool, optional): Whether to allow runs that don't have values for any segments. Defaults to False.
            cumulative (bool, optional): Whether succesive splits in a run have to add up to the total runtime. Defaults to False.
            lss_repr (bool, optional): Whether to use LSS' string representation of time (e.g. "01:55:11.1422649") or to keep the pandas.TimeDelta representation. Defaults to False.
            lss_ns (bool, optional): Whether you want to include nanoseconds in LSS' string representation of time. Defaults to True.

        Returns:
            pd.DataFrame: pandas.DataFrame of shape (n_segments, n_runs) containing run data
        """

        run_ids = self._collect_ids()
        segment_names = [segment.name for segment in self.segments]
        placeholder_data = np.full((len(segment_names), len(run_ids)), np.timedelta64("NaT", "ns"))
        placeholder_df = pd.DataFrame(placeholder_data, columns=run_ids, index=segment_names)

        for segment in self.segments:
            for split in segment.segment_history:
                if time_type == time_type.GAME_TIME:
                    time = split.game_time
                elif time_type == time_type.REAL_TIME:
                    time = split.real_time
                placeholder_df.loc[segment.name, split.id] = time

        if not allow_partial:
            # drops runs that have one or more NaT values (i.e. incomplete runs)
            placeholder_df = placeholder_df.loc[:, ~placeholder_df.isna().any()]

        if not allow_empty:
            # drops runs that only have NaT values (i.e. empty runs)
            placeholder_df = placeholder_df.loc[:, ~placeholder_df.isna().all()]

        if cumulative:
            # skipna ensures that we stop accumulating if we miss a split in beween
            placeholder_df = placeholder_df.apply(lambda column: column.cumsum(skipna=False))

        if lss_repr:
            # formats timedelta values to same string representation as used in LSS files
            placeholder_df = placeholder_df.map(
                lambda x: encode_time(x, include_ns=lss_ns) if pd.notna(x) else None
            )

        return placeholder_df
