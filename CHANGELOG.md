# CHANGELOG


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
