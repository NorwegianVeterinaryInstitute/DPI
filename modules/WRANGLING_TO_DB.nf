// Assisted by Gemini Code assistant 2025-04-02 
// Adds results to the database, one type at a time (for all pairs)
process WRANGLING_TO_DB {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    maxForks 1 // Ensure only one instance runs at a time
    debug "${params.debug}"
    label 'process_short'
    //cache 'lenient'

    input:
    path (sqlite_db) 
    val(comment)        // Comment for the database entries
    tuple val(id), path(result_file) // id sample or pair identifier depending of result provenance

    output:
    path("*.sqlite"), emit: db_path_ch
    
    script:
    """
    python ${projectDir}/bin/results_to_db.py \\
        --result_file "${result_file}" \\
        --id "${id}" \\
        --database "${sqlite_db}" \\
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
