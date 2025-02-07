# Copyright (C) 2016-2019 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

from typing import Dict, Iterable

from libversion import version_compare

from repology.logger import Logger
from repology.packagemaker import PackageFactory, PackageMaker
from repology.parsers import Parser
from repology.parsers.json import iter_json_list
from repology.transformer import PackageTransformer


class FreshcodeParser(Parser):
    def iter_parse(self, path: str, factory: PackageFactory, transformer: PackageTransformer) -> Iterable[PackageMaker]:
        result: Dict[str, PackageMaker] = {}

        # note that we actually parse database prepared by
        # fetcher, not the file we've downloaded
        for entry in iter_json_list(path, ('releases', None)):
            with factory.begin() as pkg:
                pkg.set_name(entry['name'])

                if not entry['version']:
                    pkg.log('empty version', Logger.ERROR)
                    continue

                pkg.set_version(entry['version'])

                pkg.add_homepages(entry.get('homepage'))
                pkg.set_summary(entry.get('summary'))  # cound use `or entry.get('description'))`, but it's long multiline
                #pkg.add_maintainers(entry.get('submitter') + '@freshcode')  # unfiltered garbage
                #pkg.add_downloads(entry.get('download'))  # ignore for now, may contain download page urls instead of file urls
                pkg.add_licenses(entry.get('license'))

                # take latest known versions
                if pkg.name not in result or version_compare(pkg.version, result[pkg.name].version) > 0:
                    result[pkg.name] = pkg

        yield from result.values()
