// DPI : A Nextflow pipeline that detects and reports the "Differences between Pairs of Isolates"


log.info "".center(74, "=")

log.info "############################################################################"
log.info "##     DPI: a Tool that reports Differences between Pairs of Isolates     ##"
log.info "############################################################################"
log.info "".center(74, "=")
log.info "Run track: $params.track".center(74)
log.info "DPI: $workflow.manifest.version".center(74)
log.info "".center(74, "=")

// Activate dsl2
nextflow.enable.dsl=2

// Define workflows
include { DPI } from "./workflows/DPI.nf"


workflow {
	if (params.track == "DPI") {
		DPI()
	}
}

workflow.onComplete {
	log.info "".center(74, "=")
	log.info "DPI Complete!".center(74)
	log.info "Output directory: $params.out_dir".center(74)
	log.info "Duration: $workflow.duration".center(74)
	log.info "Nextflow version: $workflow.nextflow.version".center(74)
	log.info "".center(74, "=")
}

workflow.onError {
	println "Pipeline execution stopped with the following message: ${workflow.errorMessage}".center(74, "=")
}