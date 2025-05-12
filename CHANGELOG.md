# CHANGELOG


## v1.9.0 (2025-05-12)

### Features

- Add a context to app's exceptions
  ([#32](https://github.com/e-picas/drumgizmo-kits-generator/pull/32),
  [`73f6970`](https://github.com/e-picas/drumgizmo-kits-generator/commit/73f6970f4aae63348da93f64416c4a05f5798124))

* feat: add a context to app's exceptions

* fix: make more exception tests


## v1.8.0 (2025-05-11)

### Features

- Introduce a logging file in the 'logger' module
  ([#31](https://github.com/e-picas/drumgizmo-kits-generator/pull/31),
  [`9fe433f`](https://github.com/e-picas/drumgizmo-kits-generator/commit/9fe433f1cae98ea14beeed8e0c1c5e8b688fd30d))

- Review the summary output ([#30](https://github.com/e-picas/drumgizmo-kits-generator/pull/30),
  [`5e917a9`](https://github.com/e-picas/drumgizmo-kits-generator/commit/5e917a9e08429aa21625d59d8335843d7586a8b1))


## v1.7.0 (2025-05-10)

### Build System

- Do not include 'docs' commits in changelog
  ([`5e9f399`](https://github.com/e-picas/drumgizmo-kits-generator/commit/5e9f399f46a0f877cdcddc8c1e4b8d0723e20612))

### Chores

- Review of contribution doc
  ([`586ee2b`](https://github.com/e-picas/drumgizmo-kits-generator/commit/586ee2bf872579ce1adce3c02dcb85dc42fb744d))

### Features

- Add a new option to get app's version
  ([#27](https://github.com/e-picas/drumgizmo-kits-generator/pull/27),
  [`b89ddfd`](https://github.com/e-picas/drumgizmo-kits-generator/commit/b89ddfd3b80b0521f802477f1db8b0dd1b8c8224))

- Add the version in the metadata block
  ([#26](https://github.com/e-picas/drumgizmo-kits-generator/pull/26),
  [`0fd756e`](https://github.com/e-picas/drumgizmo-kits-generator/commit/0fd756ec1d7bfa70eed30bf564cdde56687cb325))

- Large code refactoring ([#29](https://github.com/e-picas/drumgizmo-kits-generator/pull/29),
  [`167f595`](https://github.com/e-picas/drumgizmo-kits-generator/commit/167f59549e1499763a6cb2f3c6c3efa1f9edce76))

* feat: large refactorization

* ignore `TODO` on lint * move function `_strip_quotes` from `config.py` to `utils.py` * move
  function `_calculate_midi_note` from `xml_generator.py` to `utils.py` * move function
  `convert_sample_rate` from `utils.py` to `audio.py` * move function `get_audio_info` from
  `utils.py` to `audio.py` * new `utils.handle_subprocess_error` function to handle SoX errors (and
  other process errors) * move function `calculate_midi_note` from `xml_generator.py` to `utils.py`
  * new ContextManager to handle temporary directories * move function `validate_directories` from
  `main.py` to `validators.py`

* feat: large refacto 2

* all arguments parsing & printing methods moved to the new `cli.py` module * all configuration
  related methods are all in the `config.py` module

* feat: refactorization - step 3

* cleanup unsued functions * move `load_configuration` & `prepare_metadata` from `main` to `config`
  * let `config` call the transformers & validators to finally get full & validated config data

* feat: refactorization - step 4

* new `-r / --raw-output` option to strip ANSI formatting in output * add all the necessary tests to
  validate all options following `.cascade-config` specs * move the transformation of the options
  values in `transformers.py` module * do never use a default value for options outside of the
  `config.py` module

* fix: SonarQube issue

* fix: fix unused samplerate

* fix samplerate conversion of all samples * regenerate the examples/target/ samples * add a new
  script to process a generation and compare it to the example * update the Makefile with targets to
  load the script * update pre-commit config to exclude all txt files

* feat: review examples for clarity

* docs: add SPDX metadata in all scripts

* docs: review example config

* docs: review configs

* feat: new 'variations_method' param & implementation

* new parameter in the CLI * move the original volume calculation outside of the main audio files
  process * original method is now called 'linear' * implementation of a 'logarithmic' alternative *
  regeneration of the whole examples to use the 'logarithmic' method

* feat: review the 'utils.check_dependency' function

harmonize usage of the function to get a command path and test if it exists

* feat: make some cleanup

* move the `scan_source_files` function from 'cli' to 'main' module * remove unnecessary validations
  * review some outputs * regenerate the examples target

* feat: refactorization of validators & transformers

* test all rules of the specs for each option * mutualize some functions
  (i.e.`split_comma_separated`) * update the transformers & validators for robust process

* test: add tests to 'config' module

* fix: fix SonarQube issues

* feat: review of the app output

* feat: add a timer to output processing time

* fix: do not convert samples already in requested samplerate

* feat: new 'kit_generator' module

* create a new 'kit_generator' module * move all 'main' module functions (but not 'main') * move the
  related tests to a new tests file * move the 'prepare_target_directory' function from 'utils' to
  the new module

* feat: scan all audio samples when searching them (once)

* fix: wrong calculation of 'filechannels' iteration in instruments XML

* feat: centralize print & process steps in 'kit_generator' module

* feat: move the 'prepare_directories' fct to 'kit_generator'

* feat: review errors output

* feat: review the 'scan_source_file' fct

* feat: review the generate_and_compare script to include verbose mode

* fix: review of output & simplification of sources scanning

* feat: handle the case of too many source audio files

* feat: review of the midi mapping calculation

* uniformization of midi functions * load all process data in a new 'run_data' dictionnary *
  specific algo for midi note evaluation: * if the samples number is less than the midi range:
  classic * if the samples number is more, forget the 'median' and apply from start to end of range
  * in any case where the 'median' can not be user, apply above rule

* feat: introduce new 'RunData' state object

* define a dataclass 'RunData' * use it for all process data * update all functions of
  'kit_generator' to handle 'run_data' param * review of the tests to follow modifications

- New custom exceptions ([#28](https://github.com/e-picas/drumgizmo-kits-generator/pull/28),
  [`402ebb8`](https://github.com/e-picas/drumgizmo-kits-generator/commit/402ebb8dd566219486f6047ae5a0c5245170ace6))

* feat: new custom exceptions ** custom exceptions classes ** all modules should raise one of them
  in case of error ** only the main module should actually handle the errors by printing the message
  and exiting * fix: fix SonarQube issues on PR * fix: add new tests


## v1.6.0 (2025-05-04)

### Features

- Midi note info ([#24](https://github.com/e-picas/drumgizmo-kits-generator/pull/24),
  [`6215ca5`](https://github.com/e-picas/drumgizmo-kits-generator/commit/6215ca5b15e6c8107db6f403538226f13116a14b))

* feat: add the midi repartition info in dry-run mode and summary

* feat: review MIDI notes info


## v1.5.0 (2025-05-02)

### Bug Fixes

- Do not include empty metadata in drumkit.xml
  ([#19](https://github.com/e-picas/drumgizmo-kits-generator/pull/19),
  [`ed6cc7d`](https://github.com/e-picas/drumgizmo-kits-generator/commit/ed6cc7d0a46b7b6c59a3cda64c0e0519dd68cd96))

### Build System

- Makefile review with an help string
  ([#20](https://github.com/e-picas/drumgizmo-kits-generator/pull/20),
  [`9168093`](https://github.com/e-picas/drumgizmo-kits-generator/commit/91680932e71849381401cd4b2cab2eb35596e374))

### Features

- Variablize 'channels' and 'main_channels'
  ([#21](https://github.com/e-picas/drumgizmo-kits-generator/pull/21),
  [`0603d7a`](https://github.com/e-picas/drumgizmo-kits-generator/commit/0603d7afd58d5a1f68d7bff860475102d3b0265e))

### Performance Improvements

- Main.py optimization
  ([`ad2cd94`](https://github.com/e-picas/drumgizmo-kits-generator/commit/ad2cd94f0fc201068432f6e50c9152cd6776434b))


## v1.4.0 (2025-04-28)

### Bug Fixes

- Delete unused 'instrument-prefix' option
  ([#16](https://github.com/e-picas/drumgizmo-kits-generator/pull/16),
  [`ef20c20`](https://github.com/e-picas/drumgizmo-kits-generator/commit/ef20c208f7426e5406a67503e90dfdc4391d6908))

- Force uniform samplerate of samples
  ([#18](https://github.com/e-picas/drumgizmo-kits-generator/pull/18),
  [`cea74aa`](https://github.com/e-picas/drumgizmo-kits-generator/commit/cea74aa1e89175c221bf0be9be1cc2b534e8c816))

* fix: force uniform samplerate of samples

* fix: add some unit tests

### Features

- New test file formats OGG & FLAC
  ([#17](https://github.com/e-picas/drumgizmo-kits-generator/pull/17),
  [`8fb589e`](https://github.com/e-picas/drumgizmo-kits-generator/commit/8fb589e88ee41d8f18664ee2c2b525ceaa6515ed))


## v1.3.0 (2025-04-27)

### Bug Fixes

- Config values usage review ([#11](https://github.com/e-picas/drumgizmo-kits-generator/pull/11),
  [`91894d4`](https://github.com/e-picas/drumgizmo-kits-generator/commit/91894d41a2872b9003b2e91c190eac81b64ae31b))

- Delete old sonar.yml workflow
  ([`a288bb6`](https://github.com/e-picas/drumgizmo-kits-generator/commit/a288bb6fb06c7b1b61d3a8e9fbe1f53c60f9e73f))

- Fix SonarQube coverage scanner
  ([`cfd2cff`](https://github.com/e-picas/drumgizmo-kits-generator/commit/cfd2cff02c06683027e3085db4ee258f17ebca5b))

### Features

- Introduce SonarQube scanner ([#12](https://github.com/e-picas/drumgizmo-kits-generator/pull/12),
  [`1ae7711`](https://github.com/e-picas/drumgizmo-kits-generator/commit/1ae7711010c478f95dd004ac6ac6598b571f47c4))

- Introduce SonarQube scanner ([#13](https://github.com/e-picas/drumgizmo-kits-generator/pull/13),
  [`1920ef3`](https://github.com/e-picas/drumgizmo-kits-generator/commit/1920ef3032342d572c2d8769e5bed19dda2c4a2a))


## v1.2.0 (2025-04-27)

### Features

- Create a velocity-levels variable
  ([#8](https://github.com/e-picas/drumgizmo-kits-generator/pull/8),
  [`8701845`](https://github.com/e-picas/drumgizmo-kits-generator/commit/87018455fc5d1438f49d8be1003a2733a4e55813))

- Enhance config values ([#10](https://github.com/e-picas/drumgizmo-kits-generator/pull/10),
  [`bb88900`](https://github.com/e-picas/drumgizmo-kits-generator/commit/bb88900287904bf2a8af3f000caf746988bf489e))


## v1.1.2 (2025-04-27)

### Bug Fixes

- Try to update the version number in pyproject.toml
  ([`2a6bfed`](https://github.com/e-picas/drumgizmo-kits-generator/commit/2a6bfedeb2b050a678d3765bbff551ef1c499e35))


## v1.1.1 (2025-04-27)

### Bug Fixes

- Semantic-release commit message
  ([`539d293`](https://github.com/e-picas/drumgizmo-kits-generator/commit/539d293b6618b86704914db863537d71355da1d7))


## v1.1.0 (2025-04-27)

### Bug Fixes

- Try to fix semantic-release action
  ([`317f3ba`](https://github.com/e-picas/drumgizmo-kits-generator/commit/317f3ba69249ef3c7ccc3ad86fb40abc15b80fe9))

- Try to fix semantic-release action 2/2
  ([`f8026cc`](https://github.com/e-picas/drumgizmo-kits-generator/commit/f8026cc5800a9bfdee96e71da6b85af131cef8c0))

### Chores

- **ci**: Add a release step in CI
  ([#5](https://github.com/e-picas/drumgizmo-kits-generator/pull/5),
  [`fd21033`](https://github.com/e-picas/drumgizmo-kits-generator/commit/fd21033de4e7a598903ea77f491f064d6853e3b5))

### Features

- Move the code in its own directory
  ([#6](https://github.com/e-picas/drumgizmo-kits-generator/pull/6),
  [`ca1cd87`](https://github.com/e-picas/drumgizmo-kits-generator/commit/ca1cd87bbc012cca881bf1a7ef0d8a764eedd9ff))

### Testing

- New integration test based on mock contents
  ([#4](https://github.com/e-picas/drumgizmo-kits-generator/pull/4),
  [`6f33599`](https://github.com/e-picas/drumgizmo-kits-generator/commit/6f33599bfa5a9688aac734f01eda8a630a46c7fe))


## v1.0.0 (2025-04-18)

### Features

- Initial commit of the whole app
  ([`a188942`](https://github.com/e-picas/drumgizmo-kits-generator/commit/a1889423698888fecac9ae86989415c8fc21ba03))
