"""
.. module:: make_parameter_file
    :synopsis: Generates a parameter file for use with check_data_format.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy

#--------------------

def make_parameter_file(ofile, file_endings, all_file_endings):
    """
    Generates a parameter file for use with check_data_format based on the
        endings of files within the HLSP directory.

    :param ofile: The name of the output file to create.

    :type ofile: str

    :param file_endings: The unique set of file extensions among the files.

    :type file_endings: set

    :param all_file_endings: The complete set of file endings, including
        extensions.

    :type all_file_endings: set
    """

    # Convert the two sets to numpy arrays.  This allows for better indexing.
    file_endings_np = numpy.sort(numpy.asarray(list(file_endings)))

    # Define a line rule.
    hr_rule = '#' * 20

    # Write parameter file sorted by extension.
    with open(ofile, 'w') as output_file:
        # Write the format line.
        output_file.write("## Format: File Ending, Template Type, File Type,"
                          " Ignore Flag ## \n")
        for fend in file_endings_np:
            # Create the header for this extension.
            output_file.write(hr_rule + '\n')
            output_file.write("## " + fend + " ##" +  '\n')
            output_file.write(hr_rule + '\n')

            # Identify those endings that fall under this extension.
            for ending in all_file_endings:
                if fend in ending:
                    output_file.write(ending + '\n')

#--------------------
