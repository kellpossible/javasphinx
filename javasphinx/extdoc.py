#
# Copyright 2012-2015 Bronto Software, Inc. and contributors
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

import re
import os.path

from docutils import nodes, utils
from sphinx.util.nodes import split_explicit_title

def get_javadoc_ref(app, rawtext, text, fromdocname, src_package):
    javadoc_url_map = app.config.javadoc_url_map

    # Add default Java SE sources
    if not javadoc_url_map.get("java"):
        javadoc_url_map["java"] = ("http://docs.oracle.com/javase/8/docs/api", 'javadoc8')
    if not javadoc_url_map.get("javax"):
        javadoc_url_map["javax"] = ("http://docs.oracle.com/javase/8/docs/api", 'javadoc8')
    if not javadoc_url_map.get("org.xml"):
        javadoc_url_map["org.xml"] = ("http://docs.oracle.com/javase/8/docs/api", 'javadoc8')
    if not javadoc_url_map.get("org.w3c"):
        javadoc_url_map["org.w3c"] = ("http://docs.oracle.com/javase/8/docs/api", 'javadoc8')

    source = None
    package = ''
    method = None
    location = 'external'

    if '(' in text:
        # If the javadoc contains a line like this:
        # {@link #sort(List)}
        # there is no package so the text.rindex will fail
        try:
            split_point = text.rindex('.', 0, text.index('('))
            method = text[split_point + 1:]
            text = text[:split_point]
        except ValueError:
            pass

    for pkg, url_map in javadoc_url_map.items():
        baseurl = url_map[0]
        ext_type = url_map[1]

        if len(url_map) > 2:
            location = url_map[2]

        test_text = text
        if src_package is not None:
            if not test_text.startswith(pkg + '.'):
                test_text = src_package + '.' + test_text

        if test_text.startswith(pkg + '.') and len(pkg) > len(package):
            source = baseurl, ext_type
            text = test_text

    if not source:
        return None

    baseurl, ext_type = source

    if location == 'local':
        fromdocpath = os.path.dirname(fromdocname)
        baseurl = os.path.relpath(baseurl, fromdocpath)

    package_parts = []
    cls_parts = []

    for part in text.split('.'):
        if cls_parts or part[0].isupper():
            cls_parts.append(part)
        else:
            package_parts.append(part)

    package = '.'.join(package_parts)
    cls = '.'.join(cls_parts)

    if not baseurl.endswith('/'):
        baseurl = baseurl + '/'

    if ext_type == 'javadoc':
        if not cls:
            cls = 'package-summary'
        source = baseurl + package.replace('.', '/') + '/' + cls + '.html'
        if method:
            source = source + '#' + method
    elif ext_type == 'javadoc8':
        if not cls:
            cls = 'package-summary'
        source = baseurl + package.replace('.', '/') + '/' + cls + '.html'
        if method:
            source = source + '#' + re.sub(r'[()]', '-', method)
    elif ext_type == 'sphinx':
        if not cls:
            cls = 'package-index'
        source = baseurl + package.replace('.', '/') + '/' + cls.replace('.', '-') + '.html'
        if method:
            source = source + '#' + package + '.' + cls + '.' + method
    else:
        raise ValueError('invalid target specifier ' + ext_type)

    title = '.'.join(filter(None, (package, cls, method)))
    node = nodes.reference(rawtext, '')
    node['refuri'] = source
    node['reftitle'] = title

    return node