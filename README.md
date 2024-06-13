pxrd-tools
===============================================================================

[----------------------------- BADGES: BEGIN -----------------------------]: #

<table>
  <tr>
    <td>Documentation</td>
    <td>
      <a href="https://velexi-research.github.io/pxrd-tools/dev/"><img style="vertical-align: bottom;" src="https://img.shields.io/badge/docs-dev-blue.svg"/></a>
      <a href="https://velexi-research.github.io/pxrd-tools/stable/"><img style="vertical-align: bottom;" src="https://img.shields.io/badge/docs-stable-blue.svg"/></a>
    </td>
  </tr>

  <tr>
    <td>Build Status</td>
    <td>
      <a href="https://github.com/velexi-research/pxrd-tools/actions/workflows/CI.yml"><img style="vertical-align: bottom;" src="https://github.com/velexi-research/pxrd-tools/actions/workflows/CI.yml/badge.svg"/></a>
      <a href="https://codecov.io/gh/velexi-research/pxrd-tools">
        <img style="vertical-align: bottom;" src="https://codecov.io/gh/velexi-research/pxrd-tools/branch/main/graph/badge.svg"/></a>
    </td>
  </tr>

  <!-- Miscellaneous Badges -->
  <tr>
    <td colspan=2 align="center">
      <a href="https://github.com/velexi-research/pxrd-tools/issues"><img style="vertical-align: bottom;" src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"/></a>
      <a href="https://github.com/psf/black"><img style="vertical-align: bottom;" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
    </td>
  </tr>
</table>

[------------------------------ BADGES: END ------------------------------]: #

-------------------------------------------------------------------------------

The `pxrd-tools` package provides basic tools that support analysis of Powder
X-Ray Diffraction (PXRD) data.

Currently, `pxrd-tools` provides support for:

* automated peak detection.

-------------------------------------------------------------------------------

Table of Contents
-----------------

1. [Getting Started][#1]

2. [Known Issues][#2]

3. [Contributor Notes][#3]

   3.1. [License][#3.1]

   3.2. [Package Contents][#3.2]

   3.3. [Setting Up a Development Environment][#3.3]

   3.4. [Running Automated Tests][#3.4]

   3.5. [Cleaning the Development Directory][#3.5]

-------------------------------------------------------------------------------

## 1. Getting Started

1. Clone the package from the project GitHub repository:

   `https://github.com/velexi-research/pxrd-tools`.

2. Follow steps 1, 2, and 3 from [Section 3.3][#3.3] "Setting Up a Development
   Environment".

-------------------------------------------------------------------------------

## 2. Known Issues

There are currently no known issues with this package.

-------------------------------------------------------------------------------

## 3. Contributor Notes

### 3.1. License

The contents of this package are covered under the Apache License 2.0 (included
in the `LICENSE` file). The copyright for this package is contained in the
`NOTICE` file.

### 3.2. Package Contents

```
├── README.md          <- this file
├── RELEASE-NOTES.md   <- package release notes
├── LICENSE            <- package license
├── NOTICE             <- package copyright notice
├── Makefile           <- Makefile containing useful shortcuts (`make` rules).
│                         Use `make help` to show the list of available rules.
├── pyproject.toml     <- Python project metadata file
├── poetry.lock        <- Poetry lockfile
├── setup.py           <- `setup.py` script to support legacy tools that don't
│                         support pyproject.toml
├── bin/               <- scripts and programs (e.g., CLI tools)
├── docs/              <- package documentation
├── extras/            <- additional files and references that may be useful
│                         for package development
├── spikes/            <- experimental code snippets, etc.
├── src/               <- package source code
└── tests/             <- package test code
```

### 3.3. Setting Up a Development Environment

<strong><em>Note</em></strong>: this project uses `poetry` to manage Python
package dependencies.

1. Prerequisites

   * Install [Git][git].

   * Install [Python][python] 3.9 (or greater).
     <strong><em>Recommendation</em></strong>: use `pyenv` to configure the
     project to use a specific version of Python.

   * Install [Poetry][poetry] 1.2 (or greater).

   * <em>Optional</em>. Install [direnv][direnv].

2. Set up a dedicated virtual environment for the project. Any of the common
   virtual environment options (e.g., `venv`, `direnv`, `conda`) should work.
   Below are instructions for setting up a `direnv` or `poetry` environment.

   <strong><em>Note</em></strong>: to avoid conflicts between virtual
   environments, only one method should be used to manage the virtual
   environment.

   * <strong>`direnv` Environment</strong>. <em>Note</em>: `direnv` manages the
     environment for both Python and the shell.

     * Prerequisite. Install `direnv`.

     * Copy `extras/dot-envrc` to the project root directory, and rename it to
       `.envrc`.

       ```shell
       $ cd $PROJECT_ROOT_DIR
       $ cp extras/dot-envrc .envrc
       ```

     * Grant permission to direnv to execute the .envrc file.

       ```shell
       $ direnv allow
       ```

   * <strong>`poetry` Environment</strong>. <em>Note</em>: `poetry` only
     manages the Python environment (it does not manage the shell environment).

     * Create a `poetry` environment that uses a specific Python executable.
       For instance, if `python3` is on your `PATH`, the following command
       creates (or activates if it already exists) a Python virtual environment
       that uses `python3`.

       ```shell
       $ poetry env use python3
       ```

       For commands to use other Python executables for the virtual environment,
       see the [Poetry Quick Reference][poetry-quick-reference].

3. Install the Python package dependencies.

   ```shell
   $ poetry install
   ```

4. Install the git pre-commit hooks.

   ```shell
   $ pre-commit install
   ```

### 3.4. Running Automated Tests

This project is configured to support (1) automated testing of code located in
the `src` directory and (2) analysis of how well the tests cover of the source
code (i.e., coverage analysis).

* Run all of the tests.

  ```shell
  $ make test
  ```

* Run all of the tests in fail-fast mode (i.e., stop after the first failing
  test).

  ```shell
  $ make fast-test
  ```

### 3.5. Cleaning the Development Directory

* Use `make clean` to automatically remove temporary files and directories
  generated during testing (e.g., temporary directories, coverage files).

  ```shell
  $ make clean
  ```

-------------------------------------------------------------------------------

[----------------------------- INTERNAL LINKS -----------------------------]: #

[#1]: #1-getting-started

[#2]: #2-known-issues

[#3]: #3-contributor-notes
[#3.1]: #31-license
[#3.2]: #32-package-contents
[#3.3]: #33-setting-up-a-development-environment
[#3.4]: #34-running-automated-tests
[#3.5]: #35-cleaning-the-development-directory

[---------------------------- REPOSITORY LINKS ----------------------------]: #

[poetry-quick-reference]: extras/references/Poetry-Quick-Reference.md

[----------------------------- EXTERNAL LINKS -----------------------------]: #

[direnv]: https://direnv.net/

[git]: https://git-scm.com/

[python]: https://www.python.org/

[poetry]: https://python-poetry.org/
