#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>

import os
from io import StringIO
from ftplib import FTP
from unittest import TestCase, main
from urllib.request import urlopen

from odfdo.const import ODF_EXTENSIONS
from odfdo.container import odf_get_container


# Tests requiring network moved from test_container and test_document
class NetworkTest(TestCase):
    def test_http_container(self):
        file = urlopen("http://ftp.odfdo-project.net/example.odt")
        container = odf_get_container(file)
        mimetype = container.get_part("mimetype")
        self.assertEqual(mimetype, ODF_EXTENSIONS["odt"])

    def test_ftp_container(self):
        ftp = FTP("ftp.odfdo-project.net")
        ftp.login()
        file = StringIO()
        ftp.retrbinary("RETR example.odt", file.write)
        ftp.quit()
        file.seek(0)
        container = odf_get_container(file)
        mimetype = container.get_part("mimetype")
        self.assertEqual(mimetype, ODF_EXTENSIONS["odt"])

    def test_http_document(self):
        file = urlopen("http://ftp.odfdo-project.net/example.odt")
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS["odt"])

    def test_ftp_document(self):
        ftp = FTP("ftp.odfdo-project.net")
        ftp.login()
        file = StringIO()
        ftp.retrbinary("RETR example.odt", file.write)
        ftp.quit()
        file.seek(0)
        document = odf_get_document(file)
        self.assertEqual(document.get_mimetype(), ODF_EXTENSIONS["odt"])


if __name__ == "__main__":
    main()
