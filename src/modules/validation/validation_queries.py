""" SPARQL queries presented in Guizzardi, G., Fonseca, C. M., et al. (2021).
Types and taxonomic structures in conceptual modeling: A novel ontological theory and engineering support.
Data & Knowledge Engineering, 134, 101891.

These queries are used for validating the generated taxonomies with gUFO classifications.
"""

QUERY_L12 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    select distinct ?type where { { 
    select ?type (count(?type) as ?n)  
    where { 
        { ?type rdf:type gufo:Category . } 
        union { ?type rdf:type gufo:RoleMixin . } 
        union { ?type rdf:type gufo:PhaseMixin . } 
        union { ?type rdf:type gufo:Mixin . } 
        union { ?type rdf:type gufo:Kind . } 
        union { ?type rdf:type gufo:SubKind . } 
        union { ?type rdf:type gufo:Role . } 
        union { ?type rdf:type gufo:Phase . } 
    } group by ?type 
    } filter (?n > 1)}
"""

QUERY_L13 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?sortal 
    where {
        { ?sortal rdf:type gufo:SubKind . }
        union { ?sortal rdf:type gufo:Phase . }
        union { ?sortal rdf:type gufo:Role . }
    filter not exists {
    ?sortal rdfs:subClassOf* ?ultimateSortal .
    ?ultimateSortal rdf:type gufo:Kind . }}
"""

QUERY_L14 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?ultimateSortal 
    where {
        ?ultimateSortal rdf:type gufo:Kind .
    filter exists {
    ?ultimateSortal rdfs:subClassOf+/rdf:type gufo:Kind . }}
"""

QUERY_L15 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?sortal where { {
    select ?sortal (count(?sortal) as ?n)
    where {
        { ?sortal rdf:type gufo:SubKind . }
        union { ?sortal rdf:type gufo:Phase . }
        union { ?sortal rdf:type gufo:Role . }
        ?sortal rdfs:subClassOf+ ?ultimateSortal .
        ?ultimateSortal rdf:type gufo:Kind . } 
    group by ?sortal } 
    filter(?n > 1)}
"""

QUERY_L16 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?type 
    where {
        { ?type rdf:type/rdfs:subClassOf* gufo:RigidType . }
        union { ?type rdf:type/rdfs:subClassOf* gufo:SemiRigidType . }
        ?type rdfs:subClassOf+ ?antiRigidType .
        ?antiRigidType rdf:type/rdfs:subClassOf* gufo:AntiRigidType . }
"""

QUERY_L17 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?nonSortal 
    where {
        ?nonSortal rdf:type/rdfs:subClassOf* gufo:NonSortal .
        ?nonSortal rdfs:subClassOf+ ?sortal .
        ?sortal rdf:type/rdfs:subClassOf* gufo:Sortal . }
"""

QUERY_L18 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?nonSortal 
    where {
        ?nonSortal rdf:type/rdfs:subClassOf* gufo:NonSortal .
    filter not exists {{
        ?sortal rdf:type/rdfs:subClassOf* gufo:Sortal .?sortal rdfs:subClassOf* ?nonSortal .}
    union{?otherNonSortal rdf:type/rdfs:subClassOf* gufo:NonSortal .
        ?sortal rdf:type/rdfs:subClassOf* gufo:Sortal .
        ?sortal rdfs:subClassOf+ ?otherNonSortal .
        ?nonSortal rdfs:subClassOf+ ?otherNonSortal . }}}
"""

QUERIES_LIST = {
    "L12": QUERY_L12,
    "L13": QUERY_L13,
    "L14": QUERY_L14,
    "L15": QUERY_L15,
    "L16": QUERY_L16,
    "L17": QUERY_L17,
    "L18": QUERY_L18
}
