# What Is This?
This is a script for bundling small C++ projects into a single file, to upload to CodinGame, by resolving includes, include guards, and accompanying .cpp files

# How Do I Use It?
Assuming you've got python3 installed correctly, you can just run the script (located at src/bundler.py in this repo), supplying a path to the source file containing your main method, a path to the file you want the bundled code to be saved into, and prefix for identifying include-guards as command line arguments.

I.e.:

```
python3 bundler.py -i/--input <main_file> -o/--output <output_file> -g/--guard-prefix <include_guard_prefix>
```

E.g.:

```
python3 bundler.py -i main.cpp -o bundled_code.cpp -g __INCLUDE_GUARD_
```

If you omit the output argument, it will print the bundled code to standard output.

If you omit the input, it will attempt to look for a `main.cpp` file in the current directory, and, if found, will use that as the input file.

If you omit the include guard, it defaults to `__INCLUDE_GUARD`.

If you use `#pragma once`, you needn't worry about the guard prefix, and can use `-ng/--no-guard` to disable include-guard processing.

There are many more additional options available: for more detailed usage information, run the program with the `-h/--help` flag:
```
python3 bundler.py -h
```

# What Isn't It?
This script is NOT a full C++ macro preprocessor. As such, there are some caveats:
- `#define`, `#undefine`, `#ifdef`, and `#ifndef` macros that start with `__INCLUDE_GUARD_` (or another prefix you may specify as an argument) (e.g. `#indef __INCLUDE_GUARD_MY_FILE`) will be omitted from the bundled code (after being processed)
- All code between an if macro meeting the criteria in the first point and the matching end-if macro, including the opening if, and that end-if will also be omitted (this is a feature, but can controlled with cli flags)
- `#pragma once` macros are also removed (but will have been processed)
- All other macros are not processed, and are included as-is (if block nesting is safely tracked, though) - This means that, for example, `#define MY_FILE`, or `#if defined MY_FILE` would not be noticed
- A source (.cpp) file will not detected for the initial input file, as it is assumed to be a source file itself

# What Does It Actually Do, Though?
As a rough summary, it:
- Processes local `#include`s (the ones using quotes, not angle-brackets)
- Auto detects header-source (.h/.hpp - .c/.cpp) pairs, including the implementation code at the end of the relevant header file in the bundle output
- Supports `#pragma once`
- Processes include-guards and omits their contents when they are false. (but only those prefixed with either `__INCLUDE_GUARD_`, or a user-supplied guard-prefix)
- Auto-trims leading and trailing whitespace when taking from a file (thus omitting files whose contents are made empty by include guards entirely)
- Can import targets within directory paths (in both parent and child directories)
- Handles both `#ifdef` and `#ifndef` for include guards
- Ignores and reprints other preprocessor macros (including `#if`)
- Deals with nested ifs (even those it otherwise ignores)
- Can detect both .c and .cpp source files
- Auto-includes a line separator in case you don't. This line separator will be '\n' since the CG servers linux
- Optionally automatically only includes a given file

Additionally, I've included a collection of small C++ files I used to test the script into the repo to give a concrete example of how the script behaves.

They can be found in the tests directory. (and the output can be found at tests/out/bundled_code.cpp)

They were the result of running `python3 src/bundler.py -i tests/in/main.cpp -o tests/out/bundled_code.cpp` from the repository root.

# TODO
This is a tentative to-do list of additional features I've considered, but have not yet implemented.

It is not intended to be a complete list. For a more concrete idea of future plans, see the issues section.
- Code minification (with varying levels of intensity)
- CLI flags for including `#pragma` optimisation macros at the top of the bundled code
- Optionally performing some preprocessing optimisation within the script to squeeze out more performance (such as techniques described [here](https://www.codingame.com/forum/t/c-and-the-o3-compilation-flag/1670))

I'll implement these on an as-needed basis for my own use, or possibly if there are community requests for them.

Feel free to request additional features or report problems via the issues section of the repo. (or even implement changes yourself - pull-requests are welcome!)
