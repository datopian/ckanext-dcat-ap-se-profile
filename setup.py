# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    # If you are changing from the default layout of your extension, you may
    # have to change the message extractors, you can read more about babel
    # message extraction at
    # http://babel.pocoo.org/docs/messages/#extraction-method-mapping-and-configuration
    message_extractors={
        "ckanext": [
            ("**.py", "python", None),
            ("**.js", "javascript", None),
            ("**/templates/**.html", "ckan", None),
        ],
    },
    entry_points="""
        [ckan.plugins]
        dcat_ap_3_se = ckanext.dcat_ap_se_profile.plugin:DcatApSeProfilePlugin
        [ckan.rdf.profiles]
        dcat_ap_3_se_profile = ckanext.dcat_ap_se_profile.profile:SwedishDCATAP3Profile
    """,
)
