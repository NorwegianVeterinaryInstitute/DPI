def reformat_maf(file, sample, skip_rows=1):
    """ reformat the maf file after transforming from nucdiff so it can be used
        in downstream analyses

        Dependencies:
        ------------
        import re
    """
    # provide a dummy header
    maf_head = [f'track name={sample} visibility=full\n', "##maf version=1 scoring=mummer\n",
                "# mummer.v3 (SRR11262033 SRR11262179)\n", "\n"]
    maf_head = "".join(i for i in maf_head)

    # get the body
    maf_body = []

    with open(file) as input:
        # next(input) for _ in range(skip_rows)
        for _ in range(skip_rows):
            next(input)
        for line in input:
            # must be floating point
            if "score" in line:
                line = re.sub("\n", ".0\n", line)
            # not sure if required that reference is ref.1 chromosome
            # if "_" in line:
            #    line = re.sub("_", ".chr", line)
            maf_body.append(line)
    input.close()  # not sure is needed

    maf_body = "".join(i for i in maf_body)

    # write new maf file
    new_file = file.replace(".maf", "_reformated.maf")
    with open(new_file, 'w') as new:
        new.write(maf_head)
        new.write(maf_body)
    new.close()
