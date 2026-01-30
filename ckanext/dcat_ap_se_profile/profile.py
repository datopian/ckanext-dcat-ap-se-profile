import logging
from rdflib import Literal, BNode, URIRef, Namespace

from ckantoolkit import config

from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile
from ckanext.dcat.profiles.base import DCAT, VCARD, OWL, SPDX, RDF, GSP, FOAF, DCT

log = logging.getLogger(__name__)


DCTERMS = Namespace("http://purl.org/dc/terms/")


class SwedishDCATAP3Profile(EuropeanDCATAP3Profile):
    """
    DCAT AP SE 3.0 Profile
    """

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super(SwedishDCATAP3Profile, self).graph_from_dataset(dataset_dict, dataset_ref)

        # Use dcterms instead of dct (DCAT AP SE 3.0)
        self.g.bind("dcterms", DCTERMS)

        # Use dcat:version instead of owl:versionInfo
        version = dataset_dict.get("version")

        if version:
            self.g.remove((dataset_ref, OWL.versionInfo, None))
            self.g.add((dataset_ref, DCAT.version, Literal(version)))

        # Set publisher to env variable values (if all exist):
        # ckanext.dcat_ap_se_profile.publisher_name=<PUBLISHER_NAME>
        # ckanext.dcat_ap_se_profile.publisher_url=<PUBLISHER_URL>
        # ckanext.dcat_ap_se_profile.publisher_identifier=<PUBLISHER_IDENTIFIER>

        publisher_name = config.get("ckanext.dcat_ap_se_profile.publisher_name")
        publisher_url = config.get("ckanext.dcat_ap_se_profile.publisher_url")
        publisher_identifier = config.get(
            "ckanext.dcat_ap_se_profile.publisher_identifier"
        )

        if publisher_name and publisher_url and publisher_identifier:
            self.g.remove((dataset_ref, DCT.publisher, None))

            org_agents = [a for a in self.g.subjects(RDF.type, FOAF.Agent) if '/organization/' in str(a)]
            for org in org_agents:
                self.g.remove((org, None, None))
                self.g.remove((None, None, org))

            publisher_node = BNode()
            self.g.add((dataset_ref, DCTERMS.publisher, publisher_node))
            self.g.add((publisher_node, RDF.type, VCARD.Agent))
            self.g.add((publisher_node, VCARD.fn, Literal(publisher_name)))
            self.g.add(
                (publisher_node, VCARD.hasURL, URIRef(publisher_url))
            )
            self.g.add(
                (publisher_node, VCARD.identifier, URIRef(publisher_identifier))
            )

        # Retrieve contact_point_* metadata

        # Remove old contactPoint nodes
        old_contacts = list(self.g.objects(dataset_ref, DCAT.contactPoint))

        self.g.remove((dataset_ref, DCAT.contactPoint, None))

        for old_node in old_contacts:
            if isinstance(old_node, BNode):
                self.g.remove((old_node, None, None))

        contact_name = self._get_dataset_value(dataset_dict, "contact_point_name")

        if contact_name:
            contact_node = BNode()
            contact_type = self._get_dataset_value(
                dataset_dict, "contact_point_type", ""
            ).lower()

            # Default to Organization if not specified or invalid. TODO: Verify if this is the desired default.
            v_type = (
                VCARD.Organization if contact_type == "organization" else VCARD.Individual
            )

            self.g.add((contact_node, RDF.type, v_type))
            self.g.add((dataset_ref, DCAT.contactPoint, contact_node))
            self.g.add((contact_node, VCARD.fn, Literal(contact_name)))

            email = self._get_dataset_value(dataset_dict, "contact_point_email")

            if email:
                self.g.add((contact_node, VCARD.hasEmail, URIRef(self._add_mailto(email))))

            phone = self._get_dataset_value(dataset_dict, "contact_point_phone")

            if phone:
                self.g.add((contact_node, VCARD.hasTelephone, Literal(phone)))

            address = self._get_dataset_value(dataset_dict, "contact_point_address")

            if address:
                self.g.add((contact_node, VCARD.hasAddress, Literal(address)))

        # Spatial
        spatial_scheme = self._get_dataset_value(dataset_dict, "spatial_scheme")

        res_uri = (
            URIRef(spatial_scheme)
            if spatial_scheme
            else URIRef("http://www.geonames.org/2692965/CLIENTe.html")
        )
        self.g.add((dataset_ref, DCTERMS.spatial, res_uri))

        # Geo bounding box (hardcoded example from client)
        loc_node = BNode()
        self.g.add((loc_node, RDF.type, DCTERMS.Location))
        wkt = "POLYGON((12.8850967451 55.6421476735,13.1517619812 55.6421476735,13.1517619812 55.5022773196,12.8850967451 55.5022773196,12.8850967451 55.6421476735))"
        self.g.add((loc_node, DCAT.bbox, Literal(wkt, datatype=GSP.wktLiteral)))
        self.g.add((dataset_ref, DCTERMS.spatial, loc_node))

        # Distributions (resources)
        for resource_dict in dataset_dict.get("resources", []):
            dist_uri = self._get_resource_value(resource_dict, "uri")

            if not dist_uri:
                continue

            dist_ref = URIRef(dist_uri)

            # Use dcterms:format instead of dcat:mediaType
            mimetype = resource_dict.get("mimetype")

            if mimetype:
                self.g.remove((dist_ref, DCAT.mediaType, None))
                self.g.add((dist_ref, DCTERMS.format, Literal(mimetype)))

            # Remove dcterms:rights (not used in DCAT AP SE 3.0)
            self.g.remove((dist_ref, DCTERMS.rights, None))

            # SPDX checksum
            if resource_dict.get("hash"):
                for cs in self.g.objects(dist_ref, SPDX.checksum):
                    self.g.add(
                        (
                            cs,
                            SPDX.algorithm,
                            URIRef("http://spdx.org/rdf/terms#checksumAlgorithm_sha1"),
                        )
                    )

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super(SwedishDCATAP3Profile, self).graph_from_catalog(catalog_dict, catalog_ref)

        # Set catalog level publisher to env variable values (if all exist):
        # ckanext.dcat_ap_se_profile.publisher_name=<PUBLISHER_NAME>
        # ckanext.dcat_ap_se_profile.publisher_url=<PUBLISHER_URL>
        # ckanext.dcat_ap_se_profile.publisher_identifier=<PUBLISHER_IDENTIFIER>
        publisher_name = config.get("ckanext.dcat_ap_se_profile.publisher_name")
        publisher_url = config.get("ckanext.dcat_ap_se_profile.publisher_url")
        publisher_identifier = config.get(
            "ckanext.dcat_ap_se_profile.publisher_identifier"
        )

        if publisher_name and publisher_url and publisher_identifier:
            # Remove all existing agents
            agents_to_remove = []

            for agent in self.g.subjects(RDF.type, FOAF.Agent):
                if '/organization/' in str(agent):
                    agents_to_remove.append(agent)

            for agent in agents_to_remove:
                self.g.remove((agent, None, None))
                self.g.remove((None, None, agent))

            # Remove all existing publishers from the catalog
            self.g.remove((None, DCTERMS.publisher, None))

            # Set new global publisher
            publisher_node = URIRef(publisher_identifier)

            self.g.add(
                (publisher_node, RDF.type, FOAF.Agent)
            )
            self.g.add((publisher_node, FOAF.name, Literal(publisher_name)))
            self.g.add((publisher_node, FOAF.homepage, URIRef(publisher_url)))

            self.g.add((catalog_ref, DCTERMS.publisher, publisher_node))

            # Point all Datasets to the global publisher
            for dataset in self.g.subjects(RDF.type, DCAT.Dataset):
                self.g.add((dataset, DCTERMS.publisher, publisher_node))

        # Add global catalog license
        self.g.add(
            (
                catalog_ref,
                DCTERMS.license,
                URIRef("http://creativecommons.org/publicdomain/zero/1.0"),
            )
        )
