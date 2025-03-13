from copy import deepcopy
from deepdiff.summarize import summarize
from deepdiff.summarize2 import summarize as summarize2
from deepdiff.summarize3 import summarize as summarize3


class TestSummarize:

    def test_empty_dict(self):
        summary = summarize({}, max_length=50)
        assert summary == "{}", "Empty dict should be summarized as {}"

    def test_empty_list(self):
        summary = summarize([], max_length=50)
        assert summary == "[]", "Empty list should be summarized as []"

    def test_primitive_int_truncation(self):
        summary = summarize(1234567890123, max_length=10)
        # The summary should be the string representation, truncated to max_length
        assert isinstance(summary, str)
        assert len(summary) <= 10

    def test_primitive_string_no_truncation(self):
        summary = summarize("short", max_length=50)
        assert '"short"' == summary, "Short strings should not be truncated, but we are adding double quotes to it."

    def test_small_dict_summary(self):
        data = {"a": "alpha", "b": "beta"}
        summary = summarize(data, max_length=50)
        # Should be JSON-like, start with { and end with } and not exceed the max length.
        assert summary.startswith("{") and summary.endswith("}")
        assert len(summary) <= 50

    def test_long_value_truncation_in_dict(self):
        data = {
            "key1": "a" * 100,
            "key2": "b" * 50,
            "key3": "c" * 150
        }
        summary = summarize(data, max_length=100)
        summary2 = summarize2(data, max_length=100)
        summary3 = summarize3(data, max_length=100)
        # The summary should be under 100 characters and include ellipsis to indicate truncation.
        import pytest; pytest.set_trace()
        assert len(summary) <= 100
        assert "..." in summary

    def test_nested_structure_summary1(self):
        data = {
            "RecordType": "CID",
            "RecordNumber": 2719,
            "RecordTitle": "Chloroquine",
            "Section": [
                {
                    "TOCHeading": "Structures",
                    "Description": "Structure depictions and information for 2D, 3D, and crystal related",
                    "Section": [
                        {
                            "TOCHeading": "2D Structure",
                            "Description": "A two-dimensional representation of the compound",
                            "DisplayControls": {"MoveToTop": True},
                            "Information": [
                                {
                                    "ReferenceNumber": 69,
                                    "Value": {"Boolean": [True]}
                                }
                            ]
                        },
                        {
                            "TOCHeading": "3D Conformer",
                            "Description": ("A three-dimensional representation of the compound. "
                                            "The 3D structure is not experimentally determined, but computed by PubChem. "
                                            "More detailed information on this conformer model is described in the PubChem3D thematic series published in the Journal of Cheminformatics."),
                            "DisplayControls": {"MoveToTop": True},
                            "Information": [
                                {
                                    "ReferenceNumber": 69,
                                    "Description": "Chloroquine",
                                    "Value": {"Number": [2719]}
                                }
                            ]
                        }
                    ]
                },
                {
                    "TOCHeading": "Chemical Safety",
                    "Description": "Launch the Laboratory Chemical Safety Summary datasheet, and link to the safety and hazard section",
                    "DisplayControls": {"HideThisSection": True, "MoveToTop": True},
                    "Information": [
                        {
                            "ReferenceNumber": 69,
                            "Name": "Chemical Safety",
                            "Value": {
                                "StringWithMarkup": [
                                    {
                                        "String": "          ",
                                        "Markup": [
                                            {
                                                "Start": 0,
                                                "Length": 1,
                                                "URL": "https://pubchem.ncbi.nlm.nih.gov/images/ghs/GHS07.svg",
                                                "Type": "Icon",
                                                "Extra": "Irritant"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        data_copy = deepcopy(data)
        summary = summarize(data_copy, max_length=200)
        summary2 = summarize2(data_copy, max_length=200)
        summary3 = summarize3(data_copy, max_length=200)
        import pytest; pytest.set_trace()
        assert len(summary) <= 200
        # Check that some expected keys are in the summary
        assert '"RecordType"' in summary
        assert '"RecordNumber"' in summary
        assert '"RecordTitle"' in summary
        assert '{"RecordType":,"RecordNumber":,"RecordTitle":","Section":[{"TOCHeading":","Description":"St...d","Section":[{"TOCHeading":","Description":"A t,"DisplayControls":{"Information":[{}]},...]},...]}' == summary
        assert data_copy == data, "We should not have modified the original data"

    def test_nested_structure_summary2(self, compounds):
        summary = summarize(compounds, max_length=200)
        summary2 = summarize2(compounds, max_length=200)
        summary3 = summarize3(compounds, max_length=200)
        import pytest; pytest.set_trace()
        assert len(summary) <= 200
        data_copy = deepcopy(compounds)
        assert '{"RecordType":,"RecordNumber":,"RecordTitle":,"Section":[{"TOCHeading":,"Description":"Stru,"Section":[{"TOCHeading":"2D S,"DisplayControls":{}},...]},...],"Reference":[{},...]}' == summary
        assert data_copy == compounds, "We should not have modified the original data"

    def test_list_summary(self):
        data = [1, 2, 3, 4]
        summary = summarize(data, max_length=50)
        summary2 = summarize2(data, max_length=50)
        summary3 = summarize3(data, max_length=50)
        import pytest; pytest.set_trace()
        # The summary should start with '[' and end with ']'
        assert summary.startswith("[") and summary.endswith("]")
        # When more than one element exists, expect a trailing ellipsis or indication of more elements
        assert "..." not in summary

        data2 = list(range(1, 200))
        summary2 = summarize(data2, max_length=14)
        assert "..." in summary2
        expected = '[1,2,...]'
        assert expected == summary2
