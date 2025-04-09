# Unittest from gemini 2025-04-08 
import unittest
import pandas as pd
from funktions import vcf_to_df
import os

class TestVcfToDf(unittest.TestCase):

    def setUp(self):
        # Create a dummy VCF file for testing
        self.dummy_vcf_content_simple = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t100\trs123\tA\tG\t100\tPASS\tAC=1;AF=0.5;AN=2;DP=10
chr1\t101\trs456\tC\tT\t150\tPASS\tDP=15;MQ=30
"""
        with open("dummy_simple.vcf", "w") as f:
            f.write(self.dummy_vcf_content_simple)
        self.dummy_vcf_simple_path = "dummy_simple.vcf"

        self.dummy_vcf_content_complex = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t100\trs123\tA\tG,T\t100\tPASS\tAC=1,2;AF=0.5,0.5;AN=2;DP=10;SVTYPE=SNP
chr2\t200\t.\tC\tA\t90\tFILTER\tDP=5;MQ=40;SOMATIC
chr3\t300\trs789\tT\t.\t120\tPASS\tDP=20;AF=0.25;
"""
        with open("dummy_complex.vcf", "w") as f:
            f.write(self.dummy_vcf_content_complex)
        self.dummy_vcf_complex_path = "dummy_complex.vcf"

        self.dummy_vcf_with_space = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr1\t100\trs123\tA\tG\t100\tPASS\tDESC=a[space]test;AF=0.5
"""
        with open("dummy_space.vcf", "w") as f:
            f.write(self.dummy_vcf_with_space)
        self.dummy_vcf_with_space_path = "dummy_space.vcf"

        self.empty_vcf_content = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
"""
        with open("dummy_empty.vcf", "w") as f:
            f.write(self.empty_vcf_content)
        self.empty_vcf_empty_path = "dummy_empty.vcf"

    def tearDown(self):
        # Clean up the dummy VCF files
        for path in [self.dummy_vcf_simple_path, self.dummy_vcf_complex_path,
                     self.dummy_vcf_with_space_path, self.empty_vcf_empty_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_vcf_to_df_simple(self):
        df = vcf_to_df(self.dummy_vcf_simple_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 11))  # 7 base columns + 4 INFO columns
        self.assertEqual(list(df.columns), ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'AC', 'AF', 'AN', 'DP'])
        self.assertEqual(df['CHROM'].tolist(), ['chr1', 'chr1'])
        self.assertEqual(df['POS'].tolist(), [100, 101])
        self.assertEqual(df['AC'].tolist(), ['1', None])
        self.assertEqual(df['AF'].tolist(), ['0.5', None])
        self.assertEqual(df['DP'].tolist(), ['10', '15'])
        self.assertEqual(df['MQ'].tolist(), [None, '30'])

    def test_vcf_to_df_complex_multi_alt(self):
        df = vcf_to_df(self.dummy_vcf_complex_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 13))  # 7 base + 6 INFO
        self.assertIn('AC', df.columns)
        self.assertIn('AF', df.columns)
        self.assertIn('SVTYPE', df.columns)
        self.assertEqual(df['ALT'].tolist(), ['G,T', 'A', '.'])
        self.assertEqual(df['AC'].tolist(), ['1,2', None, '1'])
        self.assertEqual(df['AF'].tolist(), ['0.5,0.5', None, '0.25'])
        self.assertEqual(df['SVTYPE'].tolist(), ['SNP', 'DEL', None])
        self.assertEqual(df['SOMATIC'].tolist(), [None, 'SOMATIC', None])

    def test_vcf_to_df_with_space_replacement(self):
        df = vcf_to_df(self.dummy_vcf_with_space_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('DESC', df.columns)
        self.assertEqual(df['DESC'].iloc[0], 'a test')

    def test_vcf_to_df_empty_data(self):
        df = vcf_to_df(self.empty_vcf_empty_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (0, 7)) # Only base columns should exist

    def test_vcf_to_df_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            vcf_to_df("non_existent.vcf")

if __name__ == '__main__':
    unittest.main()