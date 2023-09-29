process INPUT {
        //conda (params.enable_conda ? 'bioconda::bakta=1.8.2' : null)
        container 'evezeyl/checkr'

        label 'process_short'

        debug "$params.debugme"

        input:
        path input

        output:
        path("unique_pairs.csv"), emit: pairs_ch 
        path("unique_samples.csv"), emit: unique_samples_ch
        file("*") 

        script:
        """
        Rscript $projectDir/bin/input_check.R --input $input
        """
}

process INPUT_VERSION {
        //conda (params.enable_conda ? 'bioconda::bakta=1.8.2' : null)
        container 'evezeyl/checkr'

         label 'process_short'   

        output:
        file("*") 

        script:
        """
        # creates the version file
        Rscript  $projectDir/bin/input_check.R --version TRUE
        """
}
