// Assisted by Gemini Code assistant 2025-04-02 
// Adds results to the database, one type at a time (for all pairs)
process WRANGLING_TO_DB {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    maxForks 1 // Ensure only one instance runs at a time
    debug "${params.debug}"
    label 'process_short_plus'

    input:
    tuple path(sqlite_db),val(comment),val(id),path(result_file)

    //output:
    //path("*.sqlite")
    
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
