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

"""Signals connector for Location."""

from .api import Location, LocationsSearch
from ..utils import extracted_data_from_ref


def enrich_location_data(sender, json=None, record=None, index=None,
                         doc_type=None, arguments=None, **dummy_kwargs):
    """Signal sent before a record is indexed.

    :param json: The dumped record dictionary which can be modified.
    :param record: The record being indexed.
    :param index: The index in which the record will be indexed.
    :param doc_type: The doc_type for the record.
    """
    if index.split('-')[0] == LocationsSearch.Meta.index:
        location = record
        if not isinstance(record, Location):
            location = Location.get_record_by_pid(record.get('pid'))
        org_pid = extracted_data_from_ref(
            location.get_library().get('organisation')
        )
        json['organisation'] = {
            'pid': org_pid
        }
