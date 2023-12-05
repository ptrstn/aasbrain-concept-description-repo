#  MIT License
#
#  Copyright (c) 2023. Mohammad Hossein Rimaz
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the “Software”), to deal in
#  the Software without restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
#  Software, and to permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
#  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from enum import Enum
from typing import Any, List, Optional, Union, Literal
from rdflib.namespace import FOAF, RDF, Namespace
import pydantic
import rdflib
from pydantic import BaseModel, Field, constr
from rdflib import Graph, XSD
from rdflib.plugins.serializers.turtle import TurtleSerializer

from app.models.aas_namespace import AASNameSpace
from app.models.has_data_specification import HasDataSpecification
from app.models.identifiable import Identifiable
from app.models.model_type import ModelType
from app.models.rdfiable import RDFiable
from app.models.reference import Reference
from app.models import base_64_url_encode


class ConceptDescription(Identifiable, HasDataSpecification, RDFiable):
    isCaseOf: Optional[List[Reference]] = Field(None, min_length=0)
    modelType: Literal["ConceptDescription"] = ModelType.ConceptDescription.value

    def to_rdf(
        self,
        graph: rdflib.Graph = None,
        parent_node: rdflib.IdentifiedNode = None,
        prefix_uri: str = "",
        base_uri: str = "",
    ) -> (rdflib.Graph, rdflib.IdentifiedNode):
        if graph == None:
            graph = rdflib.Graph()
            graph.bind("aas", AASNameSpace.AAS)
        node = rdflib.URIRef(f"{prefix_uri}{base_64_url_encode(self.id)}")
        graph.add((node, rdflib.RDF.type, AASNameSpace.AAS["ConceptDescription"]))

        # Identifiable
        # TODO: find a way to refactor
        Identifiable.append_as_rdf(self, graph, node)

        # HasDataSpecification
        HasDataSpecification.append_as_rdf(self, graph, node)

        if self.isCaseOf and len(self.isCaseOf) > 0:
            for idx, is_case in enumerate(self.isCaseOf):
                _, created_node = is_case.to_rdf(graph, node)
                graph.add((created_node, AASNameSpace.AAS["index"], rdflib.Literal(idx)))
                graph.add((node, AASNameSpace.AAS["ConceptDescription/isCaseOf"], created_node))
        return graph, node

    @staticmethod
    def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
        # Idenfiable
        identifiable = Identifiable.from_rdf(graph, subject)

        # HasDataSpecification
        hasDataSpecification = HasDataSpecification.from_rdf(graph, subject)

        isCaseOf = []
        for is_case_ref in graph.objects(subject=subject, predicate=AASNameSpace.AAS["ConceptDescription/isCaseOf"]):
            isCaseOf.append(Reference.from_rdf(graph, is_case_ref))
        if len(isCaseOf) == 0:
            isCaseOf = None

        return ConceptDescription(
            id=identifiable.id,
            administration=identifiable.administration,
            category=identifiable.category,
            idShort=identifiable.idShort,
            displayName=identifiable.displayName,
            description=identifiable.description,
            extensions=identifiable.extensions,
            isCaseOf=isCaseOf,
            embeddedDataSpecifications=hasDataSpecification.embeddedDataSpecifications,
        )
