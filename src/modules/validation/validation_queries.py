""" SPARQL queries presented in Guizzardi, G., Fonseca, C. M., et al. (2021).
Types and taxonomic structures in conceptual modeling: A novel ontological theory and engineering support.
Data & Knowledge Engineering, 134, 101891.

These queries are used for validating the generated taxonomies with gUFO classifications.
"""

""" DEFINITION:
    Every class representing an endurant type must be decorated with exactly one stereotype from the list:
    «kind», «relator», «mode», «quality», «subkind», «role», «phase», «category», «mixin», «roleMixin», «phaseMixin».
    Semi-rigid sortals are excluded from the profile.
"""
# Listing 12: Detects violations of the constraint onlyOneOntoUMLStereotype.
QUERY_L12 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
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
        union { ?type rdf:type gufo:Phase . }}
    group by ?type}
    filter (?n > 1)}
"""

""" DEFINITION:
     Every class representing an endurant sortal that is not a kind (including «subkind», «role», «phase») must
     specialize a class decorated with a stereotype «kind», «relator», «mode», or «quality».
"""
# Listing 13: Detects violations of the constraint sortalMustSpecializeUltimateSortal.
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

""" DEFINITION:
    A class representing a kind cannot specialize another kind.
"""
# Listing 14: Detects violations of the constraint ultimateSortalCantSpecializeAnother.
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

""" DEFINITION:
    A class cannot specialize more than one kind.
"""
# Listing 15: Detects violations of the constraint cantSpecializeMoreThanOneUltimateSortal.
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

""" DEFINITION:
    A class representing a rigid type («kind», «relator», «mode», «quality», «subkind», «category») cannot specialize a
    class representing an anti-rigid type («role», «phase», «roleMixin», «phaseMixin»). A class representing a semirigid
    type(«mixin») cannot specialize a class representing an anti-rigid type(«role», «phase», «roleMixin», «phaseMixin»).
"""
# Listing 16: Detects violations of the constraints:
#   rigidSortalCantSpecializeAntiRigid, rigidNonSortalCantSpecializeAntiRigid, and semiRigidCantSpecializeAntiRigid.
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

""" DEFINITION:
    A class representing a non-sortal («category», «mixin», «roleMixin», «phaseMixin») cannot specialize a class
    representing a sortal one («kind», «relator», «mode», «quality», «subkind», «role», or «phase»).
"""
# Listing 17: Detects violations of the constraint nonSortalCantSpecializeSortal.
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

""" DEFINITION:
    Given a non-sortal N, there must be a sortal S that specializes N, or specializes a non-sortal supertype common to
    both N and S.
"""
# Listing 18: Detects violations of the constraint nonSortalMustHaveSortalSpecialization.
QUERY_L18 = """
    PREFIX gufo: <http://purl.org/nemo/gufo#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select distinct ?nonSortal
    where {
        ?nonSortal rdf:type/rdfs:subClassOf* gufo:NonSortal .
    filter not exists {{
        ?sortal rdf:type/rdfs:subClassOf* gufo:Sortal .
        ?sortal rdfs:subClassOf* ?nonSortal .}
        union{?otherNonSortal rdf:type/rdfs:subClassOf* gufo:NonSortal .
        ?sortal rdf:type/rdfs:subClassOf* gufo:Sortal .
        ?sortal rdfs:subClassOf+ ?otherNonSortal .
        ?nonSortal rdfs:subClassOf+ ?otherNonSortal . }}}
"""


# This query was added because the queries available in Guizzardi (2021) do not concern relational dependency.
QUERY_R32_R33_R34 = """
PREFIX gufo: <http://purl.org/nemo/gufo#>
SELECT DISTINCT ?class_y
WHERE {
    {   ?class_y rdfs:subClassOf+ ?class_x . } .
    {   { ?class_x rdf:type gufo:Role } UNION { ?class_x rdf:type gufo:RoleMixin }  } .
    {   { ?class_y rdf:type gufo:Phase } UNION { ?class_y rdf:type gufo:PhaseMixin }  } .
}
"""

# This query was added because the queries available in Guizzardi (2021) do not concern Phase partitions.
QUERY_R35 = """
PREFIX gufo: <http://purl.org/nemo/gufo#>
SELECT DISTINCT ?class_x
WHERE {
    ?class_x rdf:type owl:Class , gufo:Phase .
    FILTER NOT EXISTS {
        ?class_y rdf:type owl:Class , gufo:Phase .
        ?class_z rdf:type owl:Class , gufo:Kind .
        ?class_x rdfs:subClassOf+ ?class_z .
        ?class_y rdfs:subClassOf+ ?class_z .
        MINUS { ?class_x rdfs:subClassOf+ ?class_y . }
        MINUS { ?class_y rdfs:subClassOf+ ?class_x . }
    }
} """

# This query was added because the queries available in Guizzardi (2021) do not concern Phase partitions.
QUERY_R37 = """
PREFIX gufo: <http://purl.org/nemo/gufo#>
SELECT DISTINCT ?class_x
WHERE {
    ?class_x rdf:type owl:Class , gufo:PhaseMixin .
    FILTER NOT EXISTS {
        ?class_y rdf:type owl:Class , gufo:PhaseMixin .
        ?class_z rdf:type owl:Class , gufo:Category .
        ?class_x rdfs:subClassOf+ ?class_z .
        ?class_y rdfs:subClassOf+ ?class_z .
        MINUS { ?class_x rdfs:subClassOf+ ?class_y . }
        MINUS { ?class_y rdfs:subClassOf+ ?class_x . }
    }
} """

# RESULTING DICTIONARIES

# Queries that only apply to OWA
QUERIES_OWA_DICT_LIST = {
    "L12": QUERY_L12,
    "L13": QUERY_L13,
    "L14": QUERY_L14,
    "L15": QUERY_L15,
    "L16": QUERY_L16,
    "L17": QUERY_L17,
    "L18": QUERY_L18,
    "R32-R34": QUERY_R32_R33_R34,
    "R35": QUERY_R35,
    "R37": QUERY_R37
}

# Queries that apply to both OWA and CWA
QUERIES_CWA_LIST = ["L13", "R35", "R37"]
