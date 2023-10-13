// trying to bypass the path problme for aptainer
//stageInMode 'copy'

// channel: get the sampleID, paths and creates a pair-key (nothing to do with ref used)
// assembly_pair_ch = Channel
// .fromPath(params.input, checkIfExists: true)
// .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
// lef map the row to values to values on the right [pair with the join, the other variables ]
// .map { row -> (pair, sample1, path1, sample2, path2) =  [ 
//         [row.sample1, row.sample2].sort().join("_"),
//         row.sample1, row.path1, row.sample2, row.path2 ]}



// creating pairs from csv files
/*input_samples_ch = INPUT.out.unique_samples_ch
                .splitCsv(header:['sample', 'path'], skip: 1, sep:",", strip:true)
                .map { row -> (sample, path) =  [ row.sample, row.path ]}
                .view()
        */

        /*
        gbff_pairs_ch = 
                input_unique_pairs_ch
                .map{it.swap(0,1)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                .map{it.swap(0,2)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                .map{it.swap(0,1)} 
                .map{it.swap(1,2)}

        vcf_annot_ch = PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
        */

csv input
SRR11262033,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR11262033.fasta,SRR11262179,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR11262179.fasta
SRR11262193,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR11262193.fasta,SRR13588432,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR13588432.fasta
SRR11262179,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR11262179.fasta,SRR13588387,/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/assemblies/SRR13588387.fasta


input_unique_pairs_ch.view()
// pair sorted by alphabetic, sample1, sample2
[SRR11262033_SRR11262179, SRR11262033, SRR11262179]
[SRR11262193_SRR13588432, SRR11262193, SRR13588432]
[SRR11262179_SRR13588387, SRR11262179, SRR13588387]


fna_pairs_ch.view()
[SRR11262033_SRR11262179, SRR11262033, SRR11262179, /cluster/work/users/evezeyl/DPI-TEST/07/f0adced4add377ff77b54a968b41d0/SRR11262033.fna, /cluster/work/users/evezeyl/DPI-TEST/6f/520c2b25312be1005991269b98cb13/SRR11262179.fna]
[SRR11262193_SRR13588432, SRR11262193, SRR13588432, /cluster/work/users/evezeyl/DPI-TEST/a3/389b43f853362639cb2d65c04ab284/SRR11262193.fna, /cluster/work/users/evezeyl/DPI-TEST/69/b6898f68fb861e5dbefa3e46e8db33/SRR13588432.fna]
[SRR11262179_SRR13588387, SRR11262179, SRR13588387, /cluster/work/users/evezeyl/DPI-TEST/6f/520c2b25312be1005991269b98cb13/SRR11262179.fna, /cluster/work/users/evezeyl/DPI-TEST/38/8fbc5431491ce0b9aff41a46f58f0b/SRR13588387.fna]


PREPARE_NUCDIFF.out.fna_ch.view() ok path of csv 
PREPARE_NUCDIFF.out.fna_ch.view() // tuple val(pair), val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch
[SRR11262033_SRR11262179, SRR11262033, /cluster/work/users/evezeyl/DPI-TEST/6f/b96115390adaec8f41ac8f0f42d85a/SRR11262033.fna, SRR11262179, /cluster/work/users/evezeyl/DPI-TEST/6f/b96115390adaec8f41ac8f0f42d85a/SRR11262179.fna]
[SRR11262193_SRR13588432, SRR11262193, /cluster/work/users/evezeyl/DPI-TEST/22/5572a98b96f768519b28a61fe62c6c/SRR11262193.fna, SRR13588432, /cluster/work/users/evezeyl/DPI-TEST/22/5572a98b96f768519b28a61fe62c6c/SRR13588432.fna]
[SRR11262179_SRR13588387, SRR11262179, /cluster/work/users/evezeyl/DPI-TEST/da/4b2be21709b1a8f5eb1a72631b1af9/SRR11262179.fna, SRR13588387, /cluster/work/users/evezeyl/DPI-TEST/da/4b2be21709b1a8f5eb1a72631b1af9/SRR13588387.fna]

# there is one too much why ? ok 
ref_query_ch.view() // pair, ref_query, ref, query
## before combining 
[SRR11262033_SRR11262179, SRR11262179_SRR11262033, SRR11262179, SRR11262033]
[SRR11262193_SRR13588432, SRR13588432_SRR11262193, SRR13588432, SRR11262193]
[SRR11262179_SRR13588387, SRR11262179_SRR13588387, SRR11262179, SRR13588387]
## after combining with PREPARE_NUCDIFF.out.fna_ch
// pair, ref_query, ref, query \ val(sample1), path(path1), val(sample2), path(path2)
[SRR11262193_SRR13588432, SRR13588432_SRR11262193, SRR13588432, SRR11262193, SRR11262193, /cluster/work/users/evezeyl/DPI-TEST/22/5572a98b96f768519b28a61fe62c6c/SRR11262193.fna, SRR13588432, /cluster/work/users/evezeyl/DPI-TEST/22/5572a98b96f768519b28a61fe62c6c/SRR13588432.fna]
[SRR11262179_SRR13588387, SRR11262179_SRR13588387, SRR11262179, SRR13588387, SRR11262179, /cluster/work/users/evezeyl/DPI-TEST/da/4b2be21709b1a8f5eb1a72631b1af9/SRR11262179.fna, SRR13588387, /cluster/work/users/evezeyl/DPI-TEST/da/4b2be21709b1a8f5eb1a72631b1af9/SRR13588387.fna]
[SRR11262033_SRR11262179, SRR11262179_SRR11262033, SRR11262179, SRR11262033, SRR11262033, /cluster/work/users/evezeyl/DPI-TEST/6f/b96115390adaec8f41ac8f0f42d85a/SRR11262033.fna, SRR11262179, /cluster/work/users/evezeyl/DPI-TEST/6f/b96115390adaec8f41ac8f0f42d85a/SRR11262179.fna]

nucdiff_vcf_ch.view()
// tuple val(pair), val(ref_query), val(ref), val(query), path("results/${ref_query}_ref_snps.vcf"), path("results/${ref_query}_query_snps.vcf"), emit: nucdiff_vcf_ch 
[SRR11262033_SRR11262179, SRR11262179_SRR11262033, SRR11262179, SRR11262033, /cluster/work/users/evezeyl/DPI-TEST/4e/615eae88e3aa905b9cbe22e3453b86/results/SRR11262179_SRR11262033_ref_snps.vcf, /cluster/work/users/evezeyl/DPI-TEST/4e/615eae88e3aa905b9cbe22e3453b86/results/SRR11262179_SRR11262033_query_snps.vcf]

PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch.view()
//  pair, ref_query, ref, query, th("${ref_query}_ref_snps_reformated.vcf"),  path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch
[SRR11262033_SRR11262179, SRR11262179_SRR11262033, SRR11262179, SRR11262033, /cluster/work/users/evezeyl/DPI-TEST/d5/8afd86f11ebc11f86557389d684a80/SRR11262179_SRR11262033_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/d5/8afd86f11ebc11f86557389d684a80/SRR11262179_SRR11262033_query_snps_reformated.vcf]
[SRR11262193_SRR13588432, SRR13588432_SRR11262193, SRR13588432, SRR11262193, /cluster/work/users/evezeyl/DPI-TEST/14/ac4fb375264357aa80bb4c47ba83c0/SRR13588432_SRR11262193_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/14/ac4fb375264357aa80bb4c47ba83c0/SRR13588432_SRR11262193_query_snps_reformated.vcf]
[SRR11262179_SRR13588387, SRR11262179_SRR13588387, SRR11262179, SRR13588387, /cluster/work/users/evezeyl/DPI-TEST/84/d344937fb592d6ad5d4994bf8f6c83/SRR11262179_SRR13588387_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/84/d344937fb592d6ad5d4994bf8f6c83/SRR11262179_SRR13588387_query_snps_reformated.vcf]



vcf_annot_ch.view()
// pair, ref_query, ref, query, refpath, querypath 
[SRR11262033_SRR11262179, SRR11262179_SRR11262033, SRR11262179, SRR11262033, /cluster/work/users/evezeyl/DPI-TEST/d5/8afd86f11ebc11f86557389d684a80/SRR11262179_SRR11262033_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/d5/8afd86f11ebc11f86557389d684a80/SRR11262179_SRR11262033_query_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/6f/520c2b25312be1005991269b98cb13/SRR11262179.gbff, /cluster/work/users/evezeyl/DPI-TEST/07/f0adced4add377ff77b54a968b41d0/SRR11262033.gbff]
[SRR11262193_SRR13588432, SRR13588432_SRR11262193, SRR13588432, SRR11262193, /cluster/work/users/evezeyl/DPI-TEST/14/ac4fb375264357aa80bb4c47ba83c0/SRR13588432_SRR11262193_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/14/ac4fb375264357aa80bb4c47ba83c0/SRR13588432_SRR11262193_query_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/69/b6898f68fb861e5dbefa3e46e8db33/SRR13588432.gbff, /cluster/work/users/evezeyl/DPI-TEST/a3/389b43f853362639cb2d65c04ab284/SRR11262193.gbff]
[SRR11262179_SRR13588387, SRR11262179_SRR13588387, SRR11262179, SRR13588387, /cluster/work/users/evezeyl/DPI-TEST/84/d344937fb592d6ad5d4994bf8f6c83/SRR11262179_SRR13588387_ref_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/84/d344937fb592d6ad5d4994bf8f6c83/SRR11262179_SRR13588387_query_snps_reformated.vcf, /cluster/work/users/evezeyl/DPI-TEST/6f/520c2b25312be1005991269b98cb13/SRR11262179.gbff, /cluster/work/users/evezeyl/DPI-TEST/38/8fbc5431491ce0b9aff41a46f58f0b/SRR13588387.gbff]


RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.view() // only output annotated vcf files 
// tuple path("${ref_query}_ref_snps_annotated.vcf"), path("${ref_query}_query_snps_annotated.vcf")
[/cluster/work/users/evezeyl/DPI-TEST/b5/1918e8830eefc3dc6403463042cb60/SRR13588432_SRR11262193_ref_snps_annotated.vcf, /cluster/work/users/evezeyl/DPI-TEST/b5/1918e8830eefc3dc6403463042cb60/SRR13588432_SRR11262193_query_snps_annotated.vcf]
[/cluster/work/users/evezeyl/DPI-TEST/76/d9e236d5f30f97a2c9f95e964819f0/SRR11262179_SRR11262033_ref_snps_annotated.vcf, /cluster/work/users/evezeyl/DPI-TEST/76/d9e236d5f30f97a2c9f95e964819f0/SRR11262179_SRR11262033_query_snps_annotated.vcf]
[/cluster/work/users/evezeyl/DPI-TEST/86/90504ef4e04ec22274aa7d92b92378/SRR11262179_SRR13588387_ref_snps_annotated.vcf, /cluster/work/users/evezeyl/DPI-TEST/86/90504ef4e04ec22274aa7d92b92378/SRR11262179_SRR13588387_query_snps_annotated.vcf]


// Database is created on recognition pattern, running on all 
