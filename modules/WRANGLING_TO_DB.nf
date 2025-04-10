// Assisted by Gemini Code assistant 2025-04-02 
// Adds results to the database, one type at a time (for all pairs)
process WRANGLING_TO_DB {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    debug "${params.debug}"
    label 'process_short'

    input:
    tuple val(index), val(comment),val(id),path(result_file)

    output:
    path "output_${index}.sqlite", emit: individual_sqlite_ch
     
    script:
    index_id = "${index}"
    output_db = "output_${index}.sqlite"
    """
    python ${projectDir}/bin/results_to_db.py \\
        --result_file "${result_file}" \\
        --id "${id}" \\
        --database "${output_db}" \\
        --comment "${comment}"
    """
}

process WRANGLING_TO_DB_VERSION{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        label 'process_short'        

        output:
        file("*") 

        script:
        """
        python ${projectDir}/bin/results_to_db.py --version > results_to_db.version
        """
}
