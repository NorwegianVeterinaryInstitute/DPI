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
    # We need to transform the way the paths are given (now that we transformed the script after ...)
    python ${projectDir}/bin/clean_list_file.py \\
         --input "${sqlite_files}" \\
         --output input_db_list.txt
  

    python ${projectDir}/bin/merge_sqlite_databases.py \\
         --output "${sqlite_db}" \\
         --input input_db_list.txt
    """
}

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
