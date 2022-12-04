# OntCatOWL-Catalog-Tester

Software used for testing OntCatOWL using the OntoUML/UFO Catalog

## Tests

The tests are performed on the [OntoUML/UFO catalog](https://github.com/unibz-core/ontouml-models) datasets
that `conformsTo` exclusively with `ontouml`.

## Tested Models
109
OntoUML only
Must have taxonomy
Minor characters modifications made for improvements
Dataset van-ee with problem


# Collected Data

## times.csv

- Total execution time
- Execution time for each rule (sum of all executions):
    - time_k_s_sup
    - time_s_k_sub
    - time_t_k_sup
    - time_ns_s_sup
    - time_s_ns_sub
    - time_r_ar_sup
    - time_ar_r_sub
    - time_ns_sub_r
    - time_ks_sf_in
    - time_n_r_t
    - time_ns_s_spe
    - time_nk_k_sup
    - time_s_nsup_k
    - time_nrs_ns_r

## Classes

### Before

- Totally unknown classes
- Partially known classes
- Totally known classes

### After

- Totally unknown classes
- Partially known classes
- Totally known classes

## Classifications

### Before

- Unknown classifications
- Known classifications

### After

- Unknown classifications
- Known classifications


## Tests

### Test 1

Executed with a single class as input. Used all classes in all datasets. Executed first in an mode and then in ac.  

The test only generates taxonomy.ttl for classes that are part of taxonomies. I.e., isolated classes are not considered when reading the original ontology.ttl file.

## Contributors

- PhD. Pedro Paulo Favato Barcelos [[GitHub]](https://github.com/pedropaulofb) [[LinkedIn]](https://www.linkedin.com/in/pedro-paulo-favato-barcelos/)
- PhD. Tiago Prince Sales [[GitHub]](https://github.com/tgoprince) [[LinkedIn]](https://www.linkedin.com/in/tiago-sales/)
- MSc. Elena Romanenko [[GitHub]](https://github.com/mozzherina) [[LinkedIn]]()
- Prof. PhD. Giancarlo Guizzardi [[LinkedIn]](https://www.linkedin.com/in/giancarlo-guizzardi-bb51aa75/)
- Eng. MSc. Gal Engelberg [[GitHub]](https://github.com/GalEngelberg) [[LinkedIn]](https://www.linkedin.com/in/gal-engelberg/)
- Prof. PhD. Dan Klein [[GitHub]](https://github.com/danklein10) [[LinkedIn]](https://www.linkedin.com/in/~danklein/)

## Acknowledgements

This work is a collaboration with Accenture Israel Cybersecurity Labs.
