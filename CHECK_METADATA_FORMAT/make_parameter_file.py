"""
.. module:: make_parameter_file
    :synopsis: Generates a parameter file for use with check_metadata_format.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy
import yaml

#--------------------

def make_parameter_file(ofile, file_endings, all_file_endings, idir):
    """
    Generates a parameter file for use with check_metadata_format based on the
        endings of files within the HLSP directory.

    :param ofile: The name of the output file to create.

    :type ofile: str

    :param file_endings: The unique set of file extensions among the files.

    :type file_endings: set

    :param all_file_endings: The complete set of file endings, including
        extensions.

    :type all_file_endings: set

    :param idir: Input directory that was run on.

    :type idir: str
    """

    # Convert the two sets to numpy arrays.  This allows for better indexing.
    file_endings_np = numpy.sort(numpy.asarray(list(file_endings)))

    # Sort all_file_endings array.
    all_file_endings_sorted = list(all_file_endings)
    all_file_endings_sorted.sort()

    # Write parameter file sorted by extension.
    with open(ofile, 'w') as output_file:
        # Construct the YAML object.
        yaml_data = {"FilePaths" : {
            'InputDir' : idir,
            'Output': ''},
                     'FileTypes' : [],
                     'KeywordUpdates' : [],
                     'UniqueParameters' : {'provenance': {'reference': ''}}
                    }

        # Add the extensions to the YAML object.
        for fend in file_endings_np:
            # Identify those endings that fall under this extension.
            for ending in all_file_endings_sorted:
                if fend in ending:
                    yaml_data['FileTypes'].append({ending:
                                                   {'Standard' : None,
                                                    'ProductType' : None,
                                                    'FileType' : None,
                                                    'RunCheck' : None,
                                                    'MRPCheck' : None,
                                                    'CAOMProductType' : None}}
                                                 )
            yaml_data.update()

        # Write YAML information to output file.
        yaml.dump(yaml_data, output_file, default_flow_style=False)

#--------------------
