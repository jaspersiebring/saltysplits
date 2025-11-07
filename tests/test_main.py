import pytest
import numpy as np
import lxml.etree as ET
from pydantic import ValidationError
from saltysplits import SaltySplits as ss
from saltysplits.enums import TimeType


class TestSaltySplits:
    def test_read_lss(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        element = tree.getroot()
        model_from_tree = ss.from_xml_tree(element)
        model_from_lss = ss.read_lss(LIVESPLIT_1_7_0)
        assert model_from_tree == model_from_lss

    def test_read_older_lss(self, LIVESPLIT_1_3):
        with pytest.raises(ValidationError):
            ss.read_lss(LIVESPLIT_1_3)

    def test_to_df(self, LIVESPLIT_1_7_0):
        splits = ss.read_lss(LIVESPLIT_1_7_0)
        splits_df = splits.to_df(
            time_type=TimeType.REAL_TIME,
            allow_partial=True,
            allow_empty=True,
            cumulative=False,
            lss_repr=False,
        )
        assert set(splits_df.columns) == set(splits._collect_ids())

    def test_to_df_cumulative(self, LIVESPLIT_1_7_0):
        splits = ss.read_lss(LIVESPLIT_1_7_0)
        cumulative_splits = splits.to_df(
            time_type=TimeType.REAL_TIME, allow_partial=False, cumulative=True, lss_repr=False
        )

        isolated_splits = splits.to_df(
            time_type=TimeType.REAL_TIME, allow_partial=False, cumulative=False, lss_repr=False
        )

        assert np.array_equal(cumulative_splits.iloc[-1, :].values, isolated_splits.sum().values)
