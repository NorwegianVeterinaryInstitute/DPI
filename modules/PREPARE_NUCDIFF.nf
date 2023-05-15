// find which isolate should be ref and provide csv out with param for next module
process PREPARE_NUCDIFF {
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //conda (params.enable_conda ? 'bioconda::chewbbaca=3.1.2' : null) // make install for that
        //container 'evezeyl/py_docker'
        
        // No need to publish execpt for debugging
        // publishDir "${params.out_dir}/PREP_NUCDIFF", mode: 'copy'

        input:
        tuple val(sample1), path(path1), val(sample2), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch
        tuple val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch

        script:
        """
        python ${params.prep_nucdiff} --fasta1 $path1 --fasta2 $path2 
        """

} 