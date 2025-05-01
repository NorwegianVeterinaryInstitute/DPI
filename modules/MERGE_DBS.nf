// Assisted by Gemini Code assistant 2025-04-02 
process MERGE_DBS {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    maxForks 1 // Ensure only one instance runs at a time
    debug "${params.debug}"
    label 'process_high_memory_time'

    input:
    path(sqlite_db)
    file sqlite_files


    script:
    """
    # Create a file containing the list of input database paths, one per line
    printf '%s\\n' ${sqlite_files} > input_db_list.txt

    python ${projectDir}/bin/merge_sqlite_databases.py \\
        --output "${sqlite_db}" \\
        --input input_db_list.txt
    """
}
// This approach suggested for robustness because nf creates a list of files and put that in a temp file
// that it simpling and passes to the python script. 
// so it needs to be explicit. 


    // mapfile input_files < ${sqlite_files}
    // python ${projectDir}/bin/merge_sqlite_databases.py \\
    //     --output "${sqlite_db}" \\
    //     --input ${input_files[@]}



process MERGE_DBS_VERSION{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        label 'process_short'        

        output:
        file("*") 

        script:
        
        """
        python ${projectDir}/bin/merge_sqlite_databases.py \\
        --version > merge_sqlite_databases.version
        """
}
