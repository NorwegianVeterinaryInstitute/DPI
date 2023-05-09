import pathlib
import re
import os
def detect_result_files(dir):
    """
    detect results files in a dir and subdirectory (for one compared pair of isolate)
    Return the path of all the files containing results to wrangle
    :dir directory in which results files have to be detected
    :returns dictionary of list file paths to analyze in different categories id(ref,query), query_files, ref_files, stat_file,
    """
    # helpers
    res_files = [str(p) for p in pathlib.Path(dir).rglob("*")]

    # should be better with case
    for f in res_files:
        if "_query_blocks.gff" in f:
            query_blocks_file = str(f)
        elif "_query_snps.gff" in f:
            query_snps_gff_file = str(f)
        elif "_query_struct.gff" in f:
            query_struct_file = str(f)
        elif "_query_additional.gff" in f:
            query_additional_file = str(f)
        elif "_query_snps_annotated.vcf" in f:
            query_snps_annotated_file = str(f)
        # ref
        elif "_ref_blocks.gff" in f:
            ref_blocks_file = str(f)
        elif "_ref_snps.gff" in f:
            ref_snps_gff_file = str(f)
        elif "_ref_struct.gff" in f:
            ref_struct_file = str(f)
        elif "_ref_additional.gff" in f:
            ref_additional_file = str(f)
        elif "_ref_snps_annotated.vcf" in f:
            ref_snps_annotated_file = str(f)
        # stat
        elif "_stat.out" in f:
            stat_file = str(f)
    stat_files = { 'stat_file': (stat_file, "_stat.out")}
    query_files = {'query_blocks' : (query_blocks_file, "_query_blocks.gff"),
                   'query_snps_gff': (query_snps_gff_file, "_query_snps.gff"),
                   'query_struct' : (query_struct_file, "_query_struct.gff"),
                   'query_additional': (query_additional_file, "_query_additional.gff")}
    ref_files = {'ref_blocks': (ref_blocks_file,"_ref_blocks.gff"),
                 'ref_snps_gff': (ref_snps_gff_file,"_ref_snps.gff"),
                 'ref_struct' : (ref_struct_file,"_ref_struct.gff"),
                 'ref_additional': (ref_additional_file,  "_ref_additional.gff")}

    annotated_vcf_files = {"ref_snps_annotated": (ref_snps_annotated_file,  "_ref_snps_annotated.vcf"),
                          "query_snps_annotated" : (query_snps_annotated_file, "_query_snps_annotated.vcf")}

    # guet the ref and query id
    prefix = re.sub("_stat.out", '', os.path.basename(stat_file))
    ref_id, query_id = re.split('_', prefix)
    id = {'ref': ref_id, 'query': query_id}

    # global dict
    files_dict = {'id': id,
                  'query_files': query_files,
                  'ref_files': ref_files,
                  'stat_files': stat_files,
                  "annotated_vcf_files": annotated_vcf_files}
    return files_dict
# test
# print(detect_results_files("/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout"))



