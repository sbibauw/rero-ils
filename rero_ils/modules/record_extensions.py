# -*- coding: utf-8 -*-
#
# RERO ILS
# Copyright (C) 2019-2022 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""RERO ILS common record extensions."""


from invenio_records.extensions import RecordExtension

from .locations.api import Location, LocationsSearch
from .utils import extracted_data_from_ref, get_base_url


class OrgLibRecordExtension(RecordExtension):
    """Defines the methods needed by an extension."""

    def pre_create(self, record):
        """Called before a record is created.

        :param record: the record metadata.
        """
        # do nothing if already exists
        if record.get('organisation') and record.get('library'):
            return
        self._add_org_and_lib(record)
        # required for validation
        if record.model:
            record.model.data = record

    def pre_commit(self, record):
        """Called before a record is committed.

        :param record: the record metadata.
        """
        self._add_org_and_lib(record)

    def _add_org_and_lib(cls, record):
        """Build $ref for the organisation and library of the item.

        :param record: the record metadata.
        """
        location_pid = extracted_data_from_ref(record.get('location'))
        # try on the elasticsearch location index
        try:
            es_loc = next(
                LocationsSearch()
                .filter('term', pid=location_pid)
                .source(['organisation', 'library'])
                .scan()
            )
            organisation_pid = es_loc.organisation.pid
            library_pid = es_loc.library.pid
        except StopIteration:
            # ok go to the db
            library = Location.get_record_by_pid(location_pid).get_library()
            library_pid = library.pid
            organisation_pid = library.organisation_pid
        url_api = '{base_url}/api/{doc_type}/{pid}'
        org_ref = {
            '$ref': url_api.format(
                base_url=get_base_url(),
                doc_type='organisations',
                pid=organisation_pid)
        }
        record['organisation'] = org_ref
        lib_ref = {
            '$ref': url_api.format(
                base_url=get_base_url(),
                doc_type='libraries',
                pid=library_pid)
        }
        record['library'] = lib_ref
