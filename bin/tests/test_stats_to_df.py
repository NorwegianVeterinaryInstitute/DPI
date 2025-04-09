# Unittest from gemini 2025-04-08 
import unittest
import pandas as pd
from funktions import stats_to_df
# import os

class TestStatsToDf(unittest.TestCase):
    def setUp(self):
        # Create a dummy stats file for testing
        self.stats_content = """Total number\t143
Insertions\t12
Deletions\t6
Substitutions\t92
Translocations\t27
Relocations\t0
Reshufflings\t0
Reshuffled blocks\t0
Inversions\t0
Unaligned sequences\t6

Uncovered ref regions num\t136
Uncovered ref regions len\t69939

DETAILED INFORMATION:
substitution\t92
gap\t0

insertion\t8
duplication\t2
tandem_duplication\t0
unaligned_beginning\t1
unaligned_end\t0
inserted_gap\t1

deletion\t5
collapsed_repeat\t1
tandem_collapsed_repeat\t0

translocation\t5
translocation-insertion\t7
translocation-insertion_ATGCN\t0
translocation-inserted_gap\t0
translocation-overlap\t15

circular_genome_start\t0
relocation\t0
relocation-insertion\t0
relocation-insertion_ATGCN\t0
relocation-inserted_gap\t0
relocation-overlap\t0


ADDITIONAL INFORMATION:
query sequences\t49
reference sequences\t116
"""
        self.file_path = "ref_query_stats.out"  # The function expects a file path
        with open(self.file_path, "w") as f:
            f.write(self.stats_content)

    def tearDown(self):
        # Clean up the dummy file after testing
        import os
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_stats_to_df(self):
        # Execute the function with the test file
        df = stats_to_df(self.file_path)

        # Assertions to validate the dataframe's structure and content
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(list(df.columns), ['param', 'value', '_REF', '_QUERY'])  # Check columns
        self.assertFalse(df.empty)  # Check not empty
        self.assertTrue(all(df['value'].notnull())) # Check no nulls in value

        # Check for specific values (this depends on the expected output)
        expected_params = ['Total number', 'Insertions', 'Deletions', 'Substitutions', 'Translocations',
                           'Relocations', 'Reshufflings', 'Reshuffled blocks', 'Inversions',
                           'Unaligned sequences', 'Uncovered ref regions num', 'Uncovered ref regions len',
                           'substitution', 'gap', 'insertion', 'duplication', 'tandem_duplication',
                           'unaligned_beginning', 'unaligned_end', 'inserted_gap', 'deletion',
                           'collapsed_repeat', 'tandem_collapsed_repeat', 'translocation',
                           'translocation-insertion', 'translocation-insertion_ATGCN',
                           'translocation-inserted_gap', 'translocation-overlap', 'circular_genome_start',
                           'relocation', 'relocation-insertion', 'relocation-insertion_ATGCN',
                           'relocation-inserted_gap', 'relocation-overlap', 'query sequences',
                           'reference sequences']
        self.assertTrue(all(param in df['param'].values for param in expected_params))
        self.assertTrue(all(df['value'].dtype == 'int64' for index,row in df.iterrows() if isinstance(row['value'], int)))

        #verify ref and query names are added
        self.assertTrue(all(df['_REF'] == 'ref'))
        self.assertTrue(all(df['_QUERY'] == 'query'))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)