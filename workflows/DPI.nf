include { PREPARE_ANNOTATE   } from "../modules/PREPARE_ANNOTATE.nf"
// include { ANNOTATE         } from "../modules/ANNOTATE.nf"
// include { PREPARE_NUCDIFF } from "../modules/PREPARE_NUCDIFF.nf"
// include { RUN_NUCDIFF      } from "../modules/RUN_NUCDIFF.nf"
// include { PREPARE_VCF_ANNOTATOR      } from "../modules/PREPARE_VCF_ANNOTATOR.nf"
// include { RUN_VCF_ANNOTATOR      } from "../modules/RUN_VCF_ANNOTATOR.nf"
// include { WRANGLING_TO_DB      } from "../modules/WRANGLING_TO_DB.nf"


workflow DPI {
	 if (!params.input) {
		exit 1, "Missing input file"
		}
	
	assembly_pair_ch = Channel
		.fromPath(params.input, checkIfExists: true)
		.splitCsv(header:true, sep:",")
		.view { row -> "${row.sample1} - ${row.path1} - ${row.sample2} - ${row.path2}" }

	// 	.map { it -> tuple(it.sample, file(it.path, checkIfExists: true)) }

	// input_list_ch = Channel
	// 	.fromPath(params.input, checkIfExists: true)
	// 	.splitCsv(header:true, sep:",")
	// 	.map { file(it.path, checkIfExists: true) }
	// 	.collect()

	// PREPARE_TABLE(input_list_ch)
	// FASTANI_VERSION()
	// FASTANI(assemblies_ch, PREPARE_TABLE.out.reflist_ch)
	
	// FASTANI.out.fastani_ch
	// 	.collectFile(name:'FASTANI_results.txt',
	// 		     storeDir:"${params.out_dir}/results")

	// REPORT_ANI(FASTANI.out.fastani_ch.collect())
}
