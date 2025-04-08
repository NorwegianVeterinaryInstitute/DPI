# Unittest from gemini 2025-04-08 
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
import os
from funktions import gff_to_df
import io

class TestGffToDf(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = "temp_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        # Clean up the temporary directory and files after tests
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def create_dummy_gff(self, file_path, content):
        with open(file_path, 'w') as f:
            f.write(content)

    def test_gff_to_df_valid(self):
        """Test with a valid GFF file."""
        valid_gff_content = """##gff-version   3
# seqname	source	feature	start	end	score	strand	frame	attribute
chr1	test	gene	1	100	.	+	.	ID=gene1;Name=test_gene
chr1	test	mRNA	10	90	.	+	.	Parent=gene1;ID=mrna1
chr1	test	exon	20	50	.	+	.	Parent=mrna1
"""
        file_path = os.path.join(self.test_dir, "ref_query.gff")
        self.create_dummy_gff(file_path, valid_gff_content)
        
        expected_df = pd.DataFrame({
            'seq_id': ['chr1', 'chr1', 'chr1'],
            'source': ['test', 'test', 'test'],
            'type': ['gene', 'mRNA', 'exon'],
            'start': [1, 10, 20],
            'end': [100, 90, 50],
            'score': [None, None, None],
            'strand': ['+', '+', '+'],
            'phase': [None, None, None],
            'ID': ['gene1', 'mrna1', None],
            'Name': ['test_gene', None, None],
            'Parent': [None, 'gene1', 'mrna1'],
            '_REF': ['ref', 'ref', 'ref'],
            '_QUERY': ['query', 'query', 'query']
        })

        result_df = gff_to_df(file_path)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_gff_to_df_empty(self):
        """Test with an empty GFF file."""
        empty_gff_content = "##gff-version   3"  # Minimal content
        file_path = os.path.join(self.test_dir, "empty.gff")
        self.create_dummy_gff(file_path, empty_gff_content)
        
        result_df = gff_to_df(file_path)
        self.assertIsNone(result_df)

    def test_gff_to_df_not_found(self):
        """Test when the GFF file is not found."""
        file_path = os.path.join(self.test_dir, "nonexistent.gff")
        
        # Capture the print output
        import sys
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        result_df = gff_to_df(file_path)
        
        sys.stdout = old_stdout  # Restore stdout
        
        self.assertIsNone(result_df)
        self.assertIn("Error: GFF file not found:", captured_output.getvalue())

    def test_gff_to_df_invalid_format(self):
        """Test with an invalid GFF format."""
        invalid_gff_content = """chr1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1"""  # Missing columns
        file_path = os.path.join(self.test_dir, "invalid.gff")
        self.create_dummy_gff(file_path, invalid_gff_content)
        
        result_df = gff_to_df(file_path)
        self.assertIsNone(result_df)

    def test_gff_to_df_one_line(self):
         """Test with a GFF file containing only one line (plus header)."""
         one_line_gff_content = """##gff-version   3\nchr1\ttest\tgene\t1\t100\t.\t+\t.\tID=gene1;Name=test_gene"""
         file_path = os.path.join(self.test_dir, "oneline.gff")
         self.create_dummy_gff(file_path, one_line_gff_content)

         result_df = gff_to_df(file_path)
         self.assertIsNone(result_df)


# Run the tests if the script is executed
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)