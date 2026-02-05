[![Tests](https://github.com//ckanext-dcat-ap-se-profile/workflows/Tests/badge.svg?branch=main)](https://github.com//ckanext-dcat-ap-se-profile/actions)

# ckanext-dcat-ap-se-profile

A CKAN extension containing a [ckanext-dcat](https://github.com/ckan/ckanext-dcat) profile for the DCAT AP 3 SE specification.

## Requirements

- CKAN 2.11+
- [ckanext-dcat](https://github.com/ckan/ckanext-dcat) (only tested on [`v2.4.2`](https://github.com/ckan/ckanext-dcat/releases/tag/v2.4.2) and later)

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | not tested    |
| 2.10            | not tested    |
| 2.11            | yes           |


## Installation

To install ckanext-dcat-ap-se-profile:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-dcat-ap-se-profile.git
    cd ckanext-dcat-ap-se-profile
    pip install -e .
	pip install -r requirements.txt

3. Add `dcat_ap_3_se` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

To use the DCAT AP 3 SE profile, add the following line to your CKAN config file:

    ckanext.dcat.rdf.profiles = dcat_ap_3_se_profile

You can also set default publisher information to be used in the RDF output (instead of the dataset organization):
    ckanext.dcat_ap_se_profile.publisher_name = <PUBLISHER_NAME>
    ckanext.dcat_ap_se_profile.publisher_url = <PUBLISHER_URL>
    ckanext.dcat_ap_se_profile.publisher_identifier = <PUBLISHER_IDENTIFIER>
    ckanext.dcat_ap_se_profile.geo_wkt = <GEO_WKT>
    ckanext.dcat_ap_se_profile.spatial_scheme_uri = <SPATIAL_SCHEME_URI>
    ckanext.dcat_ap_se_profile.catalog_description_sv = <CATALOG_DESCRIPTION_SV>
    ckanext.dcat_ap_se_profile.catalog_description_en = <CATALOG_DESCRIPTION_EN>


## Developer installation

To install ckanext-dcat-ap-se-profile for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-dcat-ap-se-profile.git
    cd ckanext-dcat-ap-se-profile
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-dcat-ap-se-profile

If ckanext-dcat-ap-se-profile should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
