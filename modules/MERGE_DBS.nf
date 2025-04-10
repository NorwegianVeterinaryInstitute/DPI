// Assisted by Gemini Code assistant 2025-04-02 
// Adds results to the database, one type at a time (for all pairs)
process MERGE_DBS {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    maxForks 1 // Ensure only one instance runs at a time
    debug "${params.debug}"
    label 'process_high_memory_time'

    input:
    path(sqlite_db)
    path(db_files)

    script:
    """
    python ${projectDir}/bin/merge_sqlite_databases.py \\
        --output "${sqlite_db}" \\
        --inputs "${db_files.join(' ')}"
    """
}

//   process MERGE_DBS {
//     input:
//     collect path(db_files)

//     output:
//     path "merged_database.sqlite"

//     script:
//     python ${projectDir}/merge_sqlite_databases.py --output "merged_database.sqlite" --inputs "${db_files.join(' ')}"
//   }

//   PARALLEL_WRITER(indexed_data_channel)
//   MERGE_DBS(PARALLEL_WRITER.out)
// }


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
