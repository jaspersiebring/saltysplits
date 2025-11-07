import pytest  # noqa: F401
import lxml.etree as ET
from saltysplits.models import Splits, Attempt, Segment, SplitTime, Time
from .conftest import drop_empty_tags


class TestSplits:
    def test_instancing(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        element = tree.getroot()

        # we currently don't model MetaData and AutosplitterSettings so we drop them before comparison
        element.remove(element.find("Metadata"))
        element.remove(element.find("AutoSplitterSettings"))

        # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
        _ = drop_empty_tags(element=element, top_level=False)
        element_string = ET.tostring(element, method="c14n2", strip_text=True).decode("utf-8")

        # validating if we can instance from known valid XML element
        model = Splits.from_xml_tree(element)
        recreated_element = model.to_xml_tree(
            exclude_unset=True
        )  # only include elements actually set by the XML
        recreated_element_string = ET.tostring(
            recreated_element, method="c14n2", strip_text=True
        ).decode("utf-8")

        # validating that encoded model is identical to original XML element
        assert element_string == recreated_element_string


class TestAttempt:
    def test_dump(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        root = tree.getroot()
        element = next(root.iter("Attempt"))
        # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
        _ = drop_empty_tags(element=element)
        element_string = ET.tostring(element, method="c14n2", strip_text=True)

        # validating if we can instance from known valid XML element
        model = Attempt.from_xml_tree(element)
        recreated_element = model.to_xml_tree(
            exclude_unset=True
        )  # only include elements actually set by the XML
        recreated_element_string = ET.tostring(recreated_element, method="c14n2", strip_text=True)

        # validating that encoded model is identical to original XML element
        assert element_string == recreated_element_string


class TestSegment:
    def test_dump(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        root = tree.getroot()
        element = next(root.iter("Segment"))
        # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
        _ = drop_empty_tags(element=element)
        element_string = ET.tostring(element, method="c14n2", strip_text=True)

        # validating if we can instance from known valid XML element
        model = Segment.from_xml_tree(element)
        recreated_element = model.to_xml_tree(
            exclude_unset=True
        )  # only include elements actually set by the XML
        recreated_element_string = ET.tostring(recreated_element, method="c14n2", strip_text=True)

        # validating that encoded model is identical to original XML element
        assert element_string == recreated_element_string


class TestSplitTime:
    def test_dump(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        root = tree.getroot()
        element = next(root.iter("SplitTime"))
        # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
        _ = drop_empty_tags(element=element)
        element_string = ET.tostring(element, method="c14n2", strip_text=True)

        # validating if we can instance from known valid XML element
        model = SplitTime.from_xml_tree(element)
        recreated_element = model.to_xml_tree(
            exclude_unset=True
        )  # only include elements actually set by the XML
        recreated_element_string = ET.tostring(recreated_element, method="c14n2", strip_text=True)

        # validating that encoded model is identical to original XML element
        assert element_string == recreated_element_string


class TestTime:
    def test_dump(self, LIVESPLIT_1_7_0):
        tree = ET.parse(LIVESPLIT_1_7_0)
        root = tree.getroot()
        element = next(root.iter("Time"))
        # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
        _ = drop_empty_tags(element=element)
        element_string = ET.tostring(element, method="c14n2", strip_text=True)

        # validating if we can instance from known valid XML element
        model = Time.from_xml_tree(element)
        recreated_element = model.to_xml_tree(
            exclude_unset=True
        )  # only include elements actually set by the XML
        recreated_element_string = ET.tostring(recreated_element, method="c14n2", strip_text=True)

        # validating that encoded model is identical to original XML element
        assert element_string == recreated_element_string
