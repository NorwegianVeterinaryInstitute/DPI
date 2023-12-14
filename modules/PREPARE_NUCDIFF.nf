process PREPARE_NUCDIFF {
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'

        label 'process_short'

        debug "$params.debug"
        tag "$pair"

        input:
        tuple val(pair), val(sample1), val(sample2), path(path1), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch
        file("*")

        script:
        """
        python $projectDir/bin/prep_nucdiff.py --fasta1 $path1 --fasta2 $path2 > $pair".sdout" 2>&1 
        """

}

process PREPARE_NUCDIFF_VERSION {
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'

        label 'process_short'
        output:
        file("*") 

        script:
        """
        python $projectDir/bin/prep_nucdiff.py --version > prep_nucdiff.version 
        """

}
