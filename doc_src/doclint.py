#!/usr/bin/env python
# Copyright 2018-2026 Jérôme Dumonteil
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
"""Script to check docstrings using griffe.

DocstringSectionParameters	"parameters"	Function parameters
DocstringSectionReturns	"returns"	Return values
DocstringSectionRaises	"raises"	Exceptions raised
DocstringSectionYields	"yields"	Generator yields
DocstringSectionReceives	"receives"	Generator receives
DocstringSectionExamples	"examples"	Usage examples
DocstringSectionAttributes	"attributes"	Class/module attributes
DocstringSectionFunctions	"functions"	Documented functions
DocstringSectionClasses	"classes"	Documented classes
DocstringSectionModules	"modules"	Documented modules
DocstringSectionTypeParameters	"typeParameters"	Type parameters
DocstringSectionOtherParameters	"otherParameters"	Keyword args
DocstringSectionWarns	"warns"	Warnings
DocstringSectionDeprecated	"deprecated"	Deprecation notice
DocstringSectionText	"text"	General text
DocstringSectionAdmonition	"admonition"	Admonitions

Available section kind values (all lowercase strings):
"text"
"parameters"
"other_parameters"
"returns"
"yields"
"receives"
"raises"
"warns"
"examples"
"attributes"
"functions"
"classes"
"modules"
"deprecated"
"admonition"
"typeParameters" (camelCase)

"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import griffe

MIN_DOC_LEN = 10
SPACER = 50
PACKAGE = "odfdo"
issues: list[str] = []


def add_issue(kind: str, obj: object, msg: str) -> None:
    issues.append(f"{kind} {obj.path:{SPACER}} - {msg}")


def print_issues() -> None:
    for issue in issues:
        print(issue)


def test_has_doc(fail: Callable, obj: Any) -> bool:
    if not obj.docstring:
        fail("missing docstring")
        return False
    return True


def get_sections(fail: Callable, obj: Any) -> Any:
    try:
        sections = obj.docstring.parse("auto")
    except Exception as e:
        fail(f"failed to parse docstring: {e}")
        return None
    return sections


def check_module(module: griffe.Module) -> None:
    def fail(msg: str) -> None:
        add_issue("O", module, msg)

    if not test_has_doc(fail, module):
        return

    get_sections(fail, module)
    # if not sections:
    #     return


def parse_modules(package: object) -> None:
    nb = len(package.modules)
    print(f"Parsing {nb} modules")
    for module in package.modules.values():
        check_module(module)


def check_class(klass: griffe.Class) -> None:
    def fail(msg: str) -> None:
        add_issue("C", klass, msg)

    if not test_has_doc(fail, klass):
        return

    sections = get_sections(fail, klass)
    if not sections:
        return

    for section in sections:
        if section.kind.value == "text" and len(section.value) < MIN_DOC_LEN:
            fail(f"description too short (<{MIN_DOC_LEN} char)")

    for member in klass.members.values():
        if member.is_function:  # Check if it's a method
            check_method(member)

    # class_obj.members	Dictionary of all class members (name → object)
    # member.is_function	Boolean check if member is a function/method
    # member.is_method	Alternative check for bound methods
    # member.docstring	The docstring object (if any)
    # member.docstring.value	Raw docstring text
    #
    # Instance methods (exclude static/class methods)
    # for name, member in class_obj.members.items():
    #     if member.is_function and not member.is_static and not member.is_classmethod:
    #         print(f"Instance method: {name}")

    # # Static methods only
    # for name, member in class_obj.members.items():
    #     if member.is_static:
    #         print(f"Static method: {name}")

    # # Class methods only
    # for name, member in class_obj.members.items():
    #     if member.is_classmethod:
    #         print(f"Class method: {name}")


def parse_classes(package: object) -> None:
    nb = len(package.classes)
    print(f"Parsing {nb} classes")
    for klass in package.classes.values():
        check_class(klass)


def check_method(meth: griffe.Method) -> None:
    def fail(msg: str) -> None:
        add_issue("E", meth, msg)

    if meth.name.startswith("_") and meth.name != "__init__":
        # do not test "_" methods
        return

    if not test_has_doc(fail, meth):
        return

    sections = get_sections(fail, meth)
    if not sections:
        return

    documented_params = set()
    has_returns = False
    has_yield = False

    for section in sections:
        if section.kind.value == "parameters":
            for param in section.value:
                name = param.name
                while name.startswith("*"):
                    name = name[1:]
                documented_params.add(name)
        elif section.kind.value == "returns":
            has_returns = True
        elif section.kind.value == "yields":
            has_yield = True

    actual_params: set = {
        p.name for p in meth.parameters if p.name not in ("self", "cls")
    }
    undocumented: set = actual_params - documented_params
    not_existing: set = documented_params - actual_params

    undocumented -= {"kwargs", "args"}

    if undocumented:
        fail(f"undocumented parameters: {', '.join(undocumented)}")
    if not_existing:
        fail(f"documented parameters not found: {', '.join(not_existing)}")
    if meth.returns and not has_returns and meth.returns != "None" and not has_yield:
        fail(f"has return type ({meth.returns}) but no return documentation")


def check_function(func: griffe.Function) -> None:
    def fail(msg: str) -> None:
        add_issue("F", func, msg)

    if not test_has_doc(fail, func):
        return

    sections = get_sections(fail, func)
    if not sections:
        return

    documented_params = set()
    has_returns = False

    for section in sections:
        if section.kind.value == "parameters":
            for param in section.value:
                documented_params.add(param.name)
        elif section.kind.value == "returns":
            has_returns = True

    actual_params = {p.name for p in func.parameters if p.name not in ("self", "cls")}
    undocumented = actual_params - documented_params
    not_existing = documented_params - actual_params

    if undocumented:
        fail(f"undocumented parameters: {', '.join(undocumented)}")
    if not_existing:
        fail(f"documented parameters not found: {', '.join(not_existing)}")
    if func.returns and not has_returns:
        fail("has return type but no return documentation")


def parse_functions(package: object) -> None:
    nb = len(package.functions)
    print(f"Parsing {nb} functions")
    for func in package.functions.values():
        check_function(func)


def main() -> None:
    package = griffe.load(PACKAGE)
    parse_modules(package)
    parse_classes(package)
    parse_functions(package)
    print_issues()


if __name__ == "__main__":
    main()
