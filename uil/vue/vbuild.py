import glob
import itertools
import os
import re
from typing import List

import vbuild


class VBuild(vbuild.VBuild):
    def __init__(self, filename, content, component):
        """ Create a VBuild class, by providing a :
                filename: which will be used to name the component, and create the namespace for the template
                content: the string buffer which contains the sfc/vue component

                Overridden to provide change some behaviour. (Like, not using a full path as unique....)

                DOES NOT SUPPORT PYTHON MODULES
        """
        if not filename:
            raise vbuild.VBuildException("Component %s should be named" % filename)

        self.component = component

        if type(content) != type(filename):  # only py2, transform
            if type(content) == vbuild.unicode:  # filename to the same type
                filename = filename.decode("utf8")  # of content to avoid
            else:  # troubles with implicit
                filename = filename.encode("utf8")  # ascii conversions (regex)

        name = os.path.splitext(os.path.basename(filename))[0]

        unique = component.name + "-" + name

        tplId = "tpl-" + unique
        dataId = "data-" + unique

        vp = vbuild.VueParser(content, filename)
        if vp.html is None:
            raise vbuild.VBuildException("Component %s doesn't have a template" % filename)
        else:
            html = re.sub(r"^<([\w-]+)", r"<\1 %s" % dataId, vp.html.value)

            self.tags = [name]
            self._html = [(tplId, html)]

            self._styles = []
            for style in vp.styles:
                self._styles.append(("", style, filename))
            for style in vp.scopedStyles:
                self._styles.append(("*[%s]" % dataId, style, filename))

            # and set self._script !
            try:
                self._script = [
                    _VueJs(name, tplId, vp.script and vp.script.value)
                ]
            except Exception as e:
                raise vbuild.VBuildException(
                    "JS Component %s contains a bad script" % filename
                )

    @property
    def script(self):
        """ Return JS (js of embbeded components), after transScript"""
        scripts = list(topological_sort(self._script))
        js = "\n".join([x.code for x in scripts])
        isPyComp = "_pyfunc_op_instantiate(" in js  # in fact : contains
        isLibInside = "var _pyfunc_op_instantiate" in js

        if (vbuild.fullPyComp is False) and isPyComp and not isLibInside:
            import pscript
            return vbuild.transScript(pscript.get_full_std_lib() + "\n" + js)
        else:
            return vbuild.transScript(js)


class _VueJs:
    """Wrapper object for the JS part of a component

    This object is new in our implementation, and implements sort capability.
    On creation time, the instance tries to figure out which other components
    this depends on by executing a regex that searches for import statements.

    These dependencies are then used by the __lt__ implementation to see if
    this module is a dependency of the other, making it necessary to load it
    earlier. If so, sorted() will place this before the other module!
    """
    IMPORT_RE = r"^import (\w+) from \S+$(?m)"

    def __init__(self, name, template_id, code):
        self.name = name
        self.template = "#" + template_id

        if code is None:
            self.js = "{}"
        else:
            p1 = code.find("{")
            p2 = code.rfind("}")
            if 0 <= p1 <= p2:
                self.js = code[p1: p2 + 1]
            else:
                raise Exception("Can't find valid content inside '{' and '}'")

        self.dependencies = set(re.findall(_VueJs.IMPORT_RE, code))

    def __repr__(self):
        return "<_VueJS: {}: {}>".format(self.name, self.dependencies)

    @property
    def code(self):
        return "var {name} = Vue.component('{name}', {code});".format(
            name=self.name,
            code=self.js.replace("{", "{\n  template:'%s'," % self.template, 1),
        )


def topological_sort(items: List[_VueJs]):
    """Sorts dependencies using a topological sort algorithm.
    In other words, makes sure that for any _VueJS, it ensures it's
    dependencies have been added before it"""
    # Set of all items that have been added already
    already_provided = set()
    while items:
        remaining_items = []

        for item in items:
            # Are all dependencies of this item provided already?
            if item.dependencies.issubset(already_provided):
                # Then yield it, and mark this item as provided
                yield item
                already_provided.add(item.name)
            else:
                # If not, retry later
                remaining_items.append(item)

        items = remaining_items


def render(component):
    """ Helpers to render VBuild's instances by providing filenames or pattern (glob's style)"""
    isPattern = lambda f: ("*" in f) or ("?" in f)

    files = []
    for i in component.get_files():
        if isinstance(i, list):
            files.extend(i)
        else:
            files.append(i)

    files = [glob.glob(i) if isPattern(i) else [i] for i in files]
    files = list(itertools.chain(*files))
    files = sorted(files, reverse=True)

    ll = []
    for f in files:
        try:
            with open(f, "r+") as fid:
                content = fid.read()
        except IOError as e:
            raise vbuild.VBuildException(str(e))
        ll.append(VBuild(f, content, component))

    return sum(ll)
