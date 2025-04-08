import unittest
import json
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

class TestJsonToDf(unittest.TestCase):
    def setUp(self):
        # Create a dummy JSON object for testing
        self.dummy_json = {
            "genome": {"name": "test_genome", "length": 1000},
            "stats": {"gc_content": 0.5, "n_contigs": 10},
            "run": {"date": "2023-01-01", "tool": "test_tool"},
            "version": {"bakta": "1.0.0", "db": "test_db"},
            "features": [
                {"id": "feature1", "type": "CDS", "location": "1-100"},
                {"id": "feature2", "type": "rRNA", "location": "200-300"},
            ],
            "sequences": [
                {
                    "seq_id": "seq1",
                    "orig_description": "len=100 cov=90 corr=80 origname=seq1 sw=test date=2023",
                    "description": "genus1 species1 gcode1 topology1",
                    "sequence": "ATGC",
                },
                {
                    "seq_id": "seq2",
                    "orig_description": "len=200 cov=190 corr=180 origname=seq2 sw=test date=2023",
                    "description": "genus2 species2 gcode2 topology2",
                    "sequence": "CGTA",
                },
            ],
        }
        self.identifier = "test_sample"

    def test_prep_info_df(self):
        expected_df = pd.DataFrame(
            {
                "name": ["test_genome"],
                "length": [1000],
                "gc_content": [0.5],
                "n_contigs": [10],
                "date": ["2023-01-01"],
                "tool": ["test_tool"],
                "bak