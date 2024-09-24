// Adds all results to the database (for all pairs)
/* process WRANGLING_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "${params.debug}"
        label 'process_high'
        cache 'lenient'
        
        input:
        val(db)
        val(comment)
        path("*")
        path("*") 
        

        output:
        path(db), emit : db_path_ch

        script:
        """
        python ${projectDir}/bin/results_to_db.py --database ${db} --comment ${comment}
        """
}  
*/

// Trial with file paths

process WRANGLING_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "${params.debug}"
        label 'process_high'
        cache 'lenient'
        
        input:
        val(db)
        val(comment)
        path(vcf_ann_paths)
        path(nucdiff_file_paths) 
        

        output:
        path(db), emit : db_path_ch

        script:
        """
        # creates the simlink for files to wrap  
        bash ${vcf_ann_paths}
        bash ${nucdiff_file_paths}

        # results to db
        python ${projectDir}/bin/results_to_db.py --database ${db} --comment ${comment}
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
