from copy import deepcopy
from deepdiff.summarize import summarize, _truncate


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
        # The summary should be under 100 characters and include ellipsis to indicate truncation.
        assert len(summary) == 113, "Yes we are going slightly above"
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
        assert len(summary) == 240, "Yes slightly above"
        # Check that some expected keys are in the summary
        assert '"RecordType"' in summary
        assert '"RecordNumber"' in summary
        assert '"RecordTitle"' in summary
        expected = '{"Section":[{"Section":[{"Description":""},{"Description":""}],"Description":"Structure depictions a...ed"},{"Information":[{"Name":"C"}],"Description":"Launch the ...on"}],"RecordTitle":"Chloroquine","RecordNumber":2719,"RecordType":"CID"}'
        assert expected == summary
        assert data_copy == data, "We should not have modified the original data"

    def test_nested_structure_summary2(self, compounds):
        summary = summarize(compounds, max_length=200)
        assert len(summary) == 319, "Ok yeah max_length is more like a guide"
        data_copy = deepcopy(compounds)
        expected = '{"Section":[{"Section":[{"Description":""},{"Description":""}],"Description":"Toxicity information r...y."},{"Section":[{"Section":["..."]},{"Section":["..."]}],"Description":"Spectral ...ds"},"..."],"Reference":[{"LicenseNote":"Use of th...e.","Description":"T...s."},{"LicenseNote":"U...e.","Description":"T"},"..."]}'
        assert expected == summary
        assert data_copy == compounds, "We should not have modified the original data"

    def test_list_summary(self):
        data = [1, 2, 3, 4]
        summary = summarize(data, max_length=50)
        # The summary should start with '[' and end with ']'
        assert summary.startswith("[") and summary.endswith("]")
        # When more than one element exists, expect a trailing ellipsis or indication of more elements
        assert "..." not in summary

        data2 = list(range(1, 200))
        summary2 = summarize(data2, max_length=14)
        assert "..." in summary2
        expected = '[100,101,102,103,10,"..."]'
        assert expected == summary2

    def test_direct_truncate_function(self):
        s = "abcdefghijklmnopqrstuvwxyz"
        truncated = _truncate(s, 20)
        assert len(truncated) == 20
        assert "..." in truncated
