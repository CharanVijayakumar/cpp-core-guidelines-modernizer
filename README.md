# C++ Core Guidelines Modernizer

**Reconstructed prototype based on Charan Vijayakumar's 2024/25 MEng Cyber Security dissertation, _Enhancing Legacy Code with C++ Core Guidelines_.** The original academic source code was lost; this repository contains a newly written implementation inspired by the documented workflow, **not the recovered original code**.

## Purpose

Analyze legacy C++ files with `clang-tidy`, write annotated copies showing diagnostics, and write separate corrected copies using supported clang-tidy fixes. Inputs are not edited.

## Features in this prototype

- Single-file and recursive directory input (`.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `.h`)
- Configurable clang-tidy checks
- Annotated output with diagnostic comments
- Separate corrected output using clang-tidy's supported fixes
- JSON summary report and basic Python unit tests

## Requirements

- Python 3.10+
- `clang-tidy` on PATH
- Optional: C++17 compiler for manually validating corrected output

## Quick start

Run from the repository root:

```bash
python -m modernizer.cli examples/legacy.cpp --output output
python -m unittest discover -s tests -v
```

Results appear in `output/annotated/`, `output/corrected/`, and `output/report.json`.

To use a compilation database for **single-file diagnostics**:

```bash
python -m modernizer.cli path/to/file.cpp --compile-db path/to/build --output output
```

**Important:** In compilation-database mode, this prototype skips auto-fixes because the copied file's location can invalidate include paths and compile flags. Multi-file compilation database remapping is future work.

## Safety and limitations

- `clang-tidy -fix` only applies fixes provided by selected checks; it cannot automatically make all code guideline-compliant.
- The prototype does not run a compilation/test gate or rollback. Review every change and compile/test corrected output before relying on it.
- Raw-pointer ownership refactoring and `malloc/free` to `new/delete` are **not** implemented as automatic transformations; such changes require semantic review.
- Diagnostic parsing uses clang-tidy's human-readable output and may need adjustment for different versions or unusual path formats.
- Analysis on headers may require extra build arguments; this prototype is best demonstrated on standalone `.cpp` files.
- Historical throughput figures in the original presentation have not been independently reproduced for this reconstruction.

## Academic context

The original dissertation describes an input handler, static analysis engine, annotation injector, auto-fix module and batch manager. This reconstruction implements a smaller, transparent subset as a starting point for further work.

## Planned improvements

- Compile database remapping for copied source trees
- Export-fixes YAML diagnostics and robust source locations
- Compile/test gates with rollback
- GitHub Actions end-to-end test using clang-tidy
- Benchmarks and richer per-check metrics

## Attribution

Project concept and original dissertation: Charan Vijayakumar, University of Limerick (2025). This source code is a fresh reconstruction; it must not be described as the original dissertation source.
