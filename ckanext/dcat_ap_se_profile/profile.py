import logging
from rdflib import Literal, BNode, URIRef, Namespace, XSD

from ckantoolkit import config

from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile
from ckanext.dcat.profiles.base import DCAT, VCARD, OWL, SPDX, RDF, GSP, FOAF, DCT
from ckanext.dcat.utils import resource_uri

log = logging.getLogger(__name__)


DCTERMS = Namespace("http://purl.org/dc/terms/")
ADMS = Namespace("http://www.w3.org/ns/adms#")
DCATAP = Namespace("http://data.europa.eu/r5r/")


class SwedishDCATAP3Profile(EuropeanDCATAP3Profile):
    """
    DCAT AP SE 3.0 Profile
    """

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super(SwedishDCATAP3Profile, self).graph_from_dataset(dataset_dict, dataset_ref)

        # Use dcterms instead of dct (DCAT AP SE 3.0)
        self.g.bind("dcterms", DCTERMS)
        self.g.bind("adms", ADMS)
        self.g.bind("dcatap", DCATAP)

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

        if publisher_url and not publisher_url.endswith('/'):
            publisher_url += '/'

        if publisher_identifier and not publisher_identifier.endswith('/'):
            publisher_identifier += '/'

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
                tele_node = BNode()
                self.g.add((contact_node, VCARD.hasTelephone, tele_node))
                self.g.add((tele_node, RDF.type, VCARD.Voice))

                digits = ''.join(filter(str.isdigit, phone))

                if digits.startswith('00'):
                    formatted = f"+{digits[2:]}"
                elif digits.startswith('0') and not digits.startswith('00'):
                    formatted = f"+46{digits[1:]}" # Default to Sweden country code
                else:
                    formatted = f"+{digits}"

                self.g.add((tele_node, VCARD.hasValue, URIRef(f"tel:{formatted}")))

            address = self._get_dataset_value(dataset_dict, "contact_point_address")

            if address:
                addr_node = BNode()
                self.g.add((contact_node, VCARD.hasAddress, addr_node))
                self.g.add((addr_node, RDF.type, VCARD.Address))
                self.g.add((addr_node, VCARD["street-address"], Literal(address)))

        # Spatial
        spatial_scheme_uri = config.get("ckanext.dcat_ap_se_profile.spatial_scheme_uri")

        if spatial_scheme_uri:
            spatial_scheme = self._get_dataset_value(dataset_dict, "spatial_scheme")

            res_uri = (
                URIRef(spatial_scheme)
                if spatial_scheme
                else URIRef(spatial_scheme_uri)
            )
            self.g.add((dataset_ref, DCTERMS.spatial, res_uri))

        # Geo bounding box (if using global value)
        geo_wkt = config.get("ckanext.dcat_ap_se_profile.geo_wkt")

        if geo_wkt:
            loc_node = BNode()
            self.g.add((loc_node, RDF.type, DCTERMS.Location))
            wkt = geo_wkt.strip()
            self.g.add((loc_node, DCAT.bbox, Literal(wkt, datatype=GSP.wktLiteral)))
            self.g.add((dataset_ref, DCTERMS.spatial, loc_node))

        # Remove existing nested nodes if necessary
        self.g.remove((dataset_ref, FOAF.page, None))

        # Distributions (resources)
        for resource_dict in dataset_dict.get("resources", []):
            dist_uri = resource_uri(resource_dict)

            if not dist_uri:
                log.error("Resource URI could not be determined for resource %s", resource_dict.get("id"))
                continue

            dist_ref = URIRef(dist_uri)

            self.g.remove((dist_ref, DCAT.mediaType, None))
            self.g.remove((dist_ref, DCT.format, None))
            self.g.remove((dist_ref, DCTERMS["format"], None))
            self.g.remove((dist_ref, FOAF.page, None))

            documentation = resource_dict.get("documentation")

            if documentation and documentation.startswith("http"):
                # Add as a direct URIRef
                self.g.add((dist_ref, FOAF.page, URIRef(documentation)))

            # Use dcterms:format instead of dcat:mediaType
            mimetype = resource_dict.get("mimetype")

            if mimetype:
                self.g.add((dist_ref, DCTERMS["format"], Literal(mimetype)))

            status = resource_dict.get("status")

            if status:
                # Status has changed to EU Publications Office URIs in AP SE 3.0
                status_mapping = {
                    "http://purl.org/adms/status/completed": "http://publications.europa.eu/resource/authority/distribution-status/COMPLETED",
                    "http://purl.org/adms/status/deprecated": "http://publications.europa.eu/resource/authority/distribution-status/DEPRECATED",
                    "http://purl.org/adms/status/underdevelopment": "http://publications.europa.eu/resource/authority/distribution-status/DEVELOP",
                    "http://purl.org/adms/status/withdrawn": "http://publications.europa.eu/resource/authority/distribution-status/WITHDRAWN",
                }
                mapped_url = status_mapping.get(status.lower())

                if mapped_url:
                    self.g.remove((dist_ref, ADMS.status, None))
                    self.g.add((dist_ref, ADMS.status, URIRef(mapped_url)))

            # Availability
            availability = resource_dict.get("availability")

            if availability:
                val = URIRef(availability) if availability.startswith("http") else Literal(availability)
                self.g.add((dist_ref, DCATAP.availability, val))

            # Remove dcterms:rights (not used in DCAT AP SE 3.0)
            self.g.remove((dist_ref, DCTERMS.rights, None))

            # SPDX checksum
            hash_val = resource_dict.get("hash")

            if hash_val:
                for cs in list(self.g.objects(dist_ref, SPDX.checksum)):
                    self.g.remove((cs, None, None))

                    self.g.add((cs, RDF.type, SPDX.Checksum))
                    self.g.add((cs, SPDX.checksumValue, Literal(hash_val, datatype=XSD.string)))
                    self.g.add(
                        (
                            cs,
                            SPDX.algorithm,
                            URIRef("http://spdx.org/rdf/terms#checksumAlgorithm_sha1"),
                        )
                    )

        # Remove empty conformsTo nodes (title, descriptions, etc.)
        for standard_node in list(self.g.objects(None, DCT.conformsTo)):
            if isinstance(standard_node, BNode):
                if not list(self.g.predicate_objects(standard_node)):
                    self.g.remove((None, DCT.conformsTo, standard_node))
                    self.g.remove((standard_node, None, None))

        # Remove empty FOAF.Document nodes (if no page, title, etc.)
        for doc_node in list(self.g.subjects(RDF.type, FOAF.Document)):
            if isinstance(doc_node, URIRef):
                if len(list(self.g.predicate_objects(doc_node))) <= 1:
                    self.g.remove((doc_node, RDF.type, FOAF.Document))


    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super(SwedishDCATAP3Profile, self).graph_from_catalog(catalog_dict, catalog_ref)

        self.g.remove((catalog_ref, DCT.language, None))
        self.g.add((catalog_ref, DCT.language, URIRef("http://publications.europa.eu/resource/authority/language/SWE")))

        catalog_description_sv = config.get("ckanext.dcat_ap_se_profile.catalog_description_sv")
        catalog_description_en = config.get("ckanext.dcat_ap_se_profile.catalog_description_en")
        catalog_title_sv = config.get("ckanext.dcat_ap_se_profile.catalog_title_sv")
        catalog_title_en = config.get("ckanext.dcat_ap_se_profile.catalog_title_en")

        self.g.remove((catalog_ref, DCT.description, None))
        self.g.add((catalog_ref, DCT.description, Literal(catalog_description_sv or "Metadatakatalog", lang="sv")))
        self.g.add((catalog_ref, DCT.description, Literal(catalog_description_en or "Metadata catalogue", lang="en")))

        self.g.remove((catalog_ref, DCT.title, None))
        self.g.add((catalog_ref, DCT.title, Literal(catalog_title_sv or "Metadatakatalog", lang="sv")))
        self.g.add((catalog_ref, DCT.title, Literal(catalog_title_en or "Metadata catalogue", lang="en")))

        # Set catalog level publisher to env variable values (if all exist):
        # ckanext.dcat_ap_se_profile.publisher_name=<PUBLISHER_NAME>
        # ckanext.dcat_ap_se_profile.publisher_url=<PUBLISHER_URL>
        # ckanext.dcat_ap_se_profile.publisher_identifier=<PUBLISHER_IDENTIFIER>
        publisher_name = config.get("ckanext.dcat_ap_se_profile.publisher_name")
        publisher_url = config.get("ckanext.dcat_ap_se_profile.publisher_url")
        publisher_identifier = config.get(
            "ckanext.dcat_ap_se_profile.publisher_identifier"
        )

        if publisher_url and not publisher_url.endswith('/'):
            publisher_url += '/'

        if publisher_identifier and not publisher_identifier.endswith('/'):
            publisher_identifier += '/'

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
