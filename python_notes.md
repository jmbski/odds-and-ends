# Python Recommendations

For a while, I'd been bumbling around with the idea of writing up some suggestions for how we
should format and standardize our Python code, but never really got around to it. Figured it'd
be better late than never, so I've collected up everything I could think of here in this document.

## Pylint & Black Formatter

These two are generally the easier to apply. The black formatter in particular, as it's just 
general formatting and applies automatically. I'm not sure there's a way with just the extension
to run it across a whole repo, so it might just be a matter of opening each file and saving (assuming
you have it set to format on save), or otherwise just applying the format.

Applying Pylint suggestions takes a little more work, as they're not automatically applied. Most
of their hints are straightforward, though, and easy enough to apply. Some you may need to look 
up the warning code ID to see why it's an issue and how to apply a fix, or if it's worth it. Of
note, if it is something that you feel isn't worth adjusting, you can disable that warning in a
module by using the syntax: `# pylint: disable=[comma separate warning names or codes]`.

For example, say you had an existing class and it was giving you a warning about 'too many public
methods', and it didn't seem worth the time to break it up. You could clear the warnings with:

```
# pylint: disable=too-many-public-methods
class SomeClassWithLotsOfFunctions:
    def __init__(self) -> None:
        # etc...

...

# Alternatively, you can use the ID number as well:

# pylint: disable=R0904
class SomeClassWithLotsOfFunctions:
    def __init__(self) -> None:
        # etc...

# Additionally, if you want to only disable it for a certain section, you can re-enable it later:
# pylint: enable=R0904

# As well, you can enable/disable multiple at once by comma or space separating them:
# pylint: disable=R0904,R0902,C0116

# And finally, you can also define a .pylintrc file to codify disabling/enabling certain rules.
# Pylint checks locally first and searches up from there, with ~/.pylintrc being the root/default
# config file it looks for. You can also specify other locations via the extension settings in
# VS Code. If you define a .pylintrc file in a project, it'll apply to all python code below it
# in the directory I believe. But usually the default settings are good enough. You can see their
# official documentation for more examples.
```

## Docstrings & Type Hints

I believe good docString formatting is key to writing professional looking and easy-to-read Python
code. Any documentation and commenting is good, of course, but I believe using a standardized 
docString format is the best approach. The AutoDocString extension should help with that, as it
defines a hot key (`ctrl + shift + 2` by default) that gathers up any relevant information in 
the class/function definition and fills it in for you. It also uses a standard format. The 
desired format can be customized, but in my opinion, the Google format (which is the default for 
AutoDocString) is the easiest to read. You can see examples of the Google docString format
throughout much of the Python code I wrote for AAA.

Another caveat to remember, is that for docStrings to appear in intellisense hints the docString
needs to be written on the line below the object in question, unlike JSDocs and other comment 
formats in other languages.

e.g.:
```
# This comment describing the function wouldn't appear in the intellisense tooltip
def some_function(some_arg: str) -> str:
    """This one would though

    Args:
        some_arg (str): A string arg

    Returns:
        str: A string response
    """    
```

And lastly, I believe it's always beneficial to add type hints in Python. They don't functionally
change anything, it's not like types in TypeScript where the typing is actually enforced.
However, they serve to make the code and intent of what's supposed to be happening significantly
easier to read. It also adds intellisense and autocomplete options by default. This applies for
function parameters as well as general variable declarations.

## General Practices

Over the past couple years, I've spent a LOT of time learning Python and trying to improve my
knowledge of it (on average, I spend more time coding at home than at work, usually around 50+
hours a week). In particular, over the last half a year or so, I've really tried to study up
on industry standard best practices and PEP documentation and shift how I write Python to be
in line with how Python itself says it should be written and structured. 

As such, I've noticed a number of habits/practices throughout our various code bases that 
should probably be shifted. Pylint will likely pick most of these up, but not all are obvious
as to why it's not a good practice or could cause problems, and some are just aesthetic of 
course.

### Mutable Default Arguments

Assigning an empty mutable object (e.g., `[]` or `{}` etc...) as default values for function
definitions is not a recommended practice and can lead to serious issues. 

In Python, functions are first class objects, and are only initialized one time when they are
first called. As such, mutable objects (which are passed as pointer references) intialized as
default values will retain that value every time the function is called. So if that default arg 
is modified, it will remain modified for every call to that function that comes later. As one
might expect, this can lead to serious, and decidedly not very apparent, issues.

It can be demonstrated easily with a simple Python example:
```
def append_len(arr: list[int] = []) -> list[int]:
    arr.append(len(arr))
    print(arr)

    return arr

append_len() # as expected, this would print `[0]`
append_len() # however, unlike other languages, this would now print: `[0, 1]`
# etc..

# additionaly, since it's a pointer reference, assigning the output and modifying that would
# ALSO modify the default
some_arr = append_len() # default is now printed as `[0, 1, 2]`
some_arr.append(3)
append_len() # default arr is defined as `[0, 1, 2, 3, 4]`
```

### Dictionary String Index Access 

This is one I see a lot in spacy at least. Using a string index accessor to retrieve a value
from a dict, i.e., `some_value = some_dict["some_key"]`. Now, strictly speaking, this isn't
on its own a bad practice. The bad practice I've seen comes from what the expected outcome 
will be. For example, I've seen a lot of snippets like:
```
    if some_dict["some_key"] is None:
        some_value = some_default
        # or some other default behavior
    else:
        some_value = some_dict["some_key"]
```

The problem arises from the fact that attempting to access a value via string index will 
raise a KeyError and crash the whole application if the key is not present. Now, sometimes,
this is the desired behavior. If that key being there is a critical part of the logic,
and its being missing is an indicator of a serious problem, you would want it to crash
and notify you so the issue can be investigated and resolved. However, many times it seems
people were expecting it to work as in JavaScript/TypeScript etc.. where a missing key
just results in an undefined/nullish value that can be handled away. But not so in Python.

In those situations, you'd want to use the `.get()` function, which safely returns a `None`
value by default if the key is missing, which then lets you gracefully handle missing keys.
`.get()` also allows you to define a default value, which is useful for, say, initializing
a class via passing it a JSON object. There is also the `defaultdict` type from the native
`collections` package. With that, you can declare a dict with a default type constructor 
that will initialize any empty values to a blank version of that type.

e.g.:
```
import os
from collections import defaultdict

def get_ext_counts(path: str) -> dict[int]:
    result = defaultdict(int)
    for root, _, files in os.walk(path):
        for file in files:
            ext = file.split(".")[-1]
            
            # you don't need to check if the key is present first before assigning,
            # or even modifying the value. If the key is not present, it will be 
            # defaulted to 0. Then incremented by 1 in either case.
            result[ext] += 1
```

### Formatting

While formatting doesn't affect the operation of the code itself, it's obviously important
for keeping code legible and human readable. There's a number of formatting areas I 
believe should be standardized across all AAA Python code, and these are based on recommendations
from Python, as well as industry standard practices. In general, the guidelines laid out
in the PEP 8 Styleguide (which can be found here: https://peps.python.org/pep-0008/) are 
what I would recommend. Here are some highlights that I've noticed to be inconsistent 
across AAA Python code:

*Naming Conventions* - We should be using the naming and case recommendations from PEP 8, i.e.,
all lower snake case for most things, all upper snake case for global constants, capitalized
camel case for class names, as well as an underscore prefix for variables intended to be
'private', despite Python not having a true private/public infrastructure. 

Additionally, names should be descriptive. In some cases, such as iterating through 
the items of a dict, using one letter variables like `for k, v in some_dict.items():` is 
fine and easily understood. But generally, using one or two letter variable names just 
makes the code harder to read later on, and understand the context of what is supposed 
to be happening. The WFS utils in spacy are a prime culprit of this. I still to this day 
don't know what 'sk' is supposed to be a reference to... But in general, the combination 
of type hints and descriptive names makes it significantly easier to maintain the code
later on.

e.g.:
```
SOME_CONST = "Some value"           # <- global constant, all upper snake

def some_function(*args) -> None:   # <- function name, snake case
    """ do stuff """
    some_local_var = "some value"   # <- variable name, snake case

class SomeClass:                    # <- class name, capitalized camel case
    """ A class that does things
    _some_private_var: str = None   # <- private variable, snake case with '_' prefix
```

*Import order* - Python import order generally doesn't affect anything, but I do believe
standardizing it will help make modules easier to determine what's what and where things
are coming from. The general precedence should be:
 - Module docstring
 - Dunder imports (objects with a double underscore, i.e. `from __future__ import annotations`)
 - Directly importing native packages (i.e., `import os`)
    - These should also typically be one line per package imported
 - 'from' imports of native packages (i.e., `from time import time`)
 - Directly importing 3rd party packages (i.e., `import pandas as pd`)
 - 'from' imports of 3rd party packages (i.e., `from tqdm import tqdm`)
 - Directly importing local code (i.e., `import local_app_utils as utils`)
 - 'from' imports of local code (i.e., `from local_app_pkgs import local_app_service`)

 Most imports should be on their own line, but when doing 'from' imports, it's generally 
 accepted to put multiple on one line to avoid verbosity, or to group them with (), e.g.:
 ```
 from my_local_pkg import (
    service_a,
    service_b,
    service_c,
    service_d,
 )
 ```

Pylint and the Black Formatter should catch most of these and auto-correct some, but I think 
it's worth being mindful of certain standards. The provided link above to the PEP 8 Styleguide 
goes into much more depth, obviously, and the formatting provided by Black is based on that
and a few other documents put out by Python.

### Project Structure

This is one where AAA is really scattered on. I'm not sure that any two apps/groups of our apps
are formatted with the same structure and/or follow the practices recommended by Python. It would
be great if AAA was able to get something like Poetry and a PEP compliant repo to push compiled
project packages to, but, alas, that's not the case and likely won't be for some time. As such,
these are some suggestions for how I'd recommend structuring our packages (not immediately, of
course). I've tried setting up packages in countless variations of form, and so far I've not
found many use cases to stray from the default recommendation from Python.

This offers a plethora of benefits, not the least of which is having a standard, understood
project structure among all AAA Python apps. Another big benefit is that it naturally 
utilizes the native path logic of Python, and thus you have fewer custom PYTHONPATH 
declarations to make. And because it uses the native pathing logic of Python, you get intellisense
hints and autocompletions for free, which makes maintenance and updates down the line wildly
easier.

In our case, however, we do generally need to account for having to use symlinks instead of 
actually imported packages. And it's import to keep those symlink imports separate. My general
recommendation is to keep them in a directory together inside the main package of the project.

The base layout recommended by Python (adjusted for our symlink situation) is something on the 
order of:

```
my_app/
├── my_app
│   ├── libs    # symlink directory. Generally, the symlinks should just be to the whole package 
│   │   │       # being imported
│   │   └── imported_symlink_pkg # e.g., `ln -s ../../../../GS_Common_U/SHC/common-python/gims_logging` 
│   │       └── # imported package code
│   ├── sub_package_a
│   │   ├── pkg_a_module_1.py
│   │   ├── pkg_a_module_2.py
│   │   └── __init__.py
│   ├── sub_package_b
│   │   ├── pkg_b_module_1.py
│   │   └── __init__.py
│   └── main.py
├── # package config files
├── pyproject.toml # e.g., a pyproject.toml if it was a package to be built
├── Dockerfile # more likely for our use cases, where the Dockerfile would live
└── README.md
```

A further benefit of this is that it makes the Dockerfile structure less complicated by an
order of magnitude. If you have all your imported symlink packages in one 'libs' package 
adjacent to your main package, you can set your PYTHONPATH with a single Dockerfile line,
i.e., `env PYTHONPATH=${PYTHONPATH}:${LIBS_DIR}`. And beyond that, if the project structure 
is the same as what it will look like in the Docker container/image, then explicit file path
construction and copying is not needed. The whole structure can be imported in with one line,
such as `COPY my_app/ /path/to/app/root/dir`, with perhaps a few extra lines for paths that 
only exist in the container, such as the models directory for Model Inference. Of course,
context matters and the structure of each project should be evaluated on its own to determine
any special case cnosiderations.