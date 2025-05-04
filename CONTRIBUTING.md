# Contributing to the "DrumGizmo Kits Generator" project

To fix a bug or make a proposal in this app, you may commit to a personal branch, push it to the repo and then
[make a pull request](https://github.com/e-picas/drumgizmo-kits-generator/compare) explaining your modification.

*   We use [`make`](https://www.gnu.org/software/make/) to run local tasks
*   Commit messages must follow the [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/)
*   The project is analyzed by [SonarCloud](https://sonarcloud.io/summary/new_code?id=e-picas_drumgizmo-kits-generator)
*   The project is built and tested by [GitHub Actions](https://github.com/e-picas/drumgizmo-kits-generator/actions)

## Get the sources

Clone this repository:

```bash
git clone https://github.com/e-picas/drumgizmo-kits-generator.git
cd drumgizmo-kits-generator
```

## Install the project

To install the `dev` dependencies and git hooks, run:

```bash
make install
```

## Code guidelines & standards

The `pre-commit` hook will try to fix your code following some standards, run the linter and tests. It is automatically run by the git hooks before each commit and a validatation of your commit message is done. These steps are run in the CI for validation.

*   We use [`black`](https://black.readthedocs.io/en/stable/) and [`isort`](https://pycqa.github.io/isort/) for codebase formatting
*   We use [`pylint`](https://pylint.readthedocs.io/en/latest/) to lint the codebase
*   We use [`pytest`](https://docs.pytest.org/en/latest/) to run the tests

## Local single tasks

Latest available `make` tasks:

```
$ make

This file is for development usage only.
To use this file, run: make <target>

  check-env       Verify that required commands are installed in the system
  clean           Cleanup Python's temporary files, cache and build
  coverage        Get the coverage analysis with `pytest`
  format          Format the code following the `.pre-commit-config.yaml` using `black` and `isort`
  generate        Generate a test kit to `tests/target_test/` from `examples/sources/` and compare it with `examples/target/`
  install         Install the app's dependencies & git hooks
  lint            Run the linter with `pylint`
  test            Run the tests in `tests/` with `pytest`

To get a list of all available targets, you can use Make auto-completion: 'make <TAB><TAB>' or read the Makefile file.
```
