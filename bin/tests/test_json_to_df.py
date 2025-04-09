# Unittest from gemini 2025-04-08 
import unittest
import pandas as pd
import numpy as np
from funktions import json_to_df 
class TestJsonToDf(unittest.TestCase):

    # Sample JSON data for testing
    sample_json = {
        "genome": {"genome_id": "123", "genome_name": "TestGenome"},
        "stats": {"total_genes": 1000, "coding_genes": 900},
        "run": {"start_time": "2024-01-01", "end_time": "2024-01-02"},
        "version": {"bakta": "1.5.0"},
        "features": [{"feature_id": "f1", "type": "gene", "location": "1..100"},
                     {"feature_id": "f2", "type": "CDS", "location": "200..300"}],
        "sequences": [{"sequence_id": "s1", "length": 10000, "description": "Escherichia coli K12 MG1655 complete genome", "orig_description": "len=10000 cov=20x corr=yes origname=NC_000913 sw=bwa date=2024-01-01"},
                      {"sequence_id": "s2", "length": 5000, "description": "Salmonella enterica Typhimurium SL1344 complete genome", "orig_description": "len=5000 cov=30x corr=yes origname=NC_003197 sw=bwa date=2024-01-01"}]
    }

    def test_prep_info_df(self):
        """Tests the prep_info_df function."""

        info_df = json_to_df.prep_info_df(self.sample_json, "sample1")

        # Assert that the output is a DataFrame
        self.assertIsInstance(info_df, pd.DataFrame)

        # Assert that the DataFrame has the correct columns
        expected_columns = ['identifier', 'genome_genome_id', 'genome_genome_name', 'stats_total_genes', 'stats_coding_genes', 'run_start_time', 'run_end_time', 'version_bakta']
        self.assertListEqual(list(info_df.columns), expected_columns)

        # Assert that the identifier column is correctly added
        self.assertTrue('identifier' in info_df.columns)
        self.assertTrue(all(info_df['identifier'] == 'sample1'))

        # Check for correct data types (important for potential database interactions)
        self.assertTrue(pd.api.types.is_string_dtype(info_df['identifier']))
        self.assertTrue(pd.api.types.is_string_dtype(info_df['genome_genome_name']))
        self.assertTrue(pd.api.types.is_integer_dtype(info_df['stats_total_genes']))

    def test_prep_features_df(self):
        """Tests the prep_features_df function."""

        features_df = json_to_df.prep_features_df(self.sample_json, "sample1")

        # Assert that the output is a DataFrame
        self.assertIsInstance(features_df, pd.DataFrame)

        # Assert that the DataFrame has the correct columns
        expected_columns = ['identifier', 'feature_id', 'type', 'location']
        self.assertListEqual(list(features_df.columns), expected_columns)

        # Assert that all values are strings
        self.assertTrue(all(features_df.apply(lambda col: col.apply(lambda x: isinstance(x, str))).all()))

        # Assert identifier column is correctly added
        self.assertTrue('identifier' in features_df.columns)
        self.assertTrue(all(features_df['identifier'] == 'sample1'))

    def test_prep_sequences_df(self):
        """Tests the prep_sequences_df function."""

        sequences_df = json_to_df.prep_sequences_df(self.sample_json, "sample1")

        # Assert that the output is a DataFrame
        self.assertIsInstance(sequences_df, pd.DataFrame)

        # Assert that the DataFrame has the correct columns
        expected_columns = ['identifier', 'sequence_id', 'length', 'description', 'len', 'cov', 'corr', 'origname', 'sw', 'date', 'genus', 'species', 'gcode', 'topology']
        self.assertListEqual(list(sequences_df.columns), expected_columns)

        # Assert that the 'len' column exists after splitting
        self.assertTrue('len' in sequences_df.columns)

        # Check for object type after string operations
        self.assertTrue(pd.api.types.is_object_dtype(sequences_df['len']))

        # Assert identifier column
        self.assertTrue('identifier' in sequences_df.columns)
        self.assertTrue(all(sequences_df['identifier'] == 'sample1'))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)