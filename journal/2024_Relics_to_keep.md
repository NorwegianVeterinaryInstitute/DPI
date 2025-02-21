// Trial with file paths

process WRANGLING_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "${params.debug}"
        //label 'process_high_memory_time'
        cache 'lenient'
        // process becomes linear 
        maxForks 1

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

        vcf_ann_file_ch = 
                RUN_VCF_ANNOTATOR.out.annotated_vcf_ch
                .collect()
                .flatten()
                .map{it -> "ln -s " + it.toString() + " ." }
                .collectFile(name: 'vcf_ann_paths.sh', newLine: true)

        
        nucdiff_file_ch = 
                RUN_NUCDIFF.out.nucdiff_res_ch
                .collect()
                .flatten()
                .map{it -> "ln -s " + it.toString() + " ." }
                .collectFile(name: 'nucdiff_file_paths.sh', newLine: true)     */    

        //nucdiff_file_ch.view()


        // WRANGLING_TO_DB(db_path_ch, comment_ch, vcf_ann_file_ch, nucdiff_file_ch)