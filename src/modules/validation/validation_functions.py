""" Main functions regarding validations. """

import glob, os

def validate_gufo_taxonomies ():
    """ Performs validation on all generated gufo taxonomies and generates a csv output file with the results. """

    # Iterate over all taxonomy files with gUFO classifications
    os.chdir("catalog")
    for file in glob.glob("**/*.ttl", recursive=True):
        print(file)
        pass




