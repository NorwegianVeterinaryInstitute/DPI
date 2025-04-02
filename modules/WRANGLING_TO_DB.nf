// Assisted by Gemini Code assistant 2025-04-02 
// Adds results to the database, one type at a time (for all pairs)
process WRANGLING_TO_DB {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    maxForks 1 // Ensure only one instance runs at a time
    debug "${params.debug}"
    label 'process_high'
    cache 'lenient'

    input:
    val(db)             // Path to the SQLite database
    val(comment)        // Comment for the database entries
    tuple val(pair), val(result_type), path(result_files) // Pair identifier, result type, and files of that type

    output:
    path(db), emit: db_path_ch // Emit the database path after processing

    script:
    """
    python ${projectDir}/bin/results_to_db.py \\
        --database ${db} \\
        --comment "${comment}" \\
        --pair "${pair}" \\
        --result_type "${result_type}" \\
        --result_files "${result_files.join(',')}"
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
