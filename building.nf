nextflow.enable.dsl=2
DPIDIR="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI"

params.input= "${DPIDIR}/assets/pairsheet_local.csv"
// Annotation options
//baktaDB         = "/run/media/evezeyl/4T/DATABASES/bakta/db" //cliff
//trainingFILE    = "/run/media/evezeyl/4T/DATABASES/Listeria_monocytogenes.trn" //cliff
params.baktaDB         = "/mnt/blue/DATA/BIOINFO_LOCAL/bakta_database/db" //work
params.training        = "/mnt/blue/DATA/BIOINFO_LOCAL/Listeria_monocytogenes.trn" //work
params.genus           = "Listeria"
params.species         = "monocytogenes"





// process splitLetters {
//   output:
//     path 'chunk_*'

//   """
//   printf '${params.str}' | split -b 6 - chunk_
//   """
// }

process ANNOTATE {
        // for testing
        conda '/home/vi2067/.conda/envs/bakta'

        input:
        tuple val(sample1), file(path1), val(sample2), file(path2)
        path baktaDB
        path training
        val genus
        val species

        output:
        file("*")
        //path "reflist.txt", emit: reflist_ch

        shell:
        """
        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}


workflow {
	 if (!params.input) {
		exit 1, "Missing input file"
		}
	
	assembly_pair_ch = Channel
		.fromPath(params.input, checkIfExists: true)
		//.splitCsv(header:true, sep:",") # for some reason not working
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map {row -> tuple(row.sample1, file(row.path1), row.sample2, file(row.path2))}
        ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)
    
        }