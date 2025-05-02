# CHANGELOG


## v1.5.0 (2025-05-02)

### Bug Fixes

- Do not include empty metadata in drumkit.xml
  ([#19](https://github.com/e-picas/drumgizmo-kits-generator/pull/19),
  [`ed6cc7d`](https://github.com/e-picas/drumgizmo-kits-generator/commit/ed6cc7d0a46b7b6c59a3cda64c0e0519dd68cd96))

### Build System

- Makefile review with an help string
  ([#20](https://github.com/e-picas/drumgizmo-kits-generator/pull/20),
  [`9168093`](https://github.com/e-picas/drumgizmo-kits-generator/commit/91680932e71849381401cd4b2cab2eb35596e374))

### Documentation

- Auto-generated config file for Claude 3.7 Sonnet [skip ci]
  ([`e1bea78`](https://github.com/e-picas/drumgizmo-kits-generator/commit/e1bea78dd726e5554ba79fe7e68709bf327f9443))

- Ini variables lowercase (for readability)
  ([`0d3a621`](https://github.com/e-picas/drumgizmo-kits-generator/commit/0d3a621269e7a466b782589d63fdaafb20e07244))

- New GitHub templates for issues & PRs [skip ci]
  ([`52b34ed`](https://github.com/e-picas/drumgizmo-kits-generator/commit/52b34ed1b01074a177e9ab77e81e98c4e0dbd34f))

- Update README.md [skip ci]
  ([`675a240`](https://github.com/e-picas/drumgizmo-kits-generator/commit/675a24042c29ae7e75ab2649239f3a893cdbc58b))

- Update README.md [skip ci]
  ([`d42617b`](https://github.com/e-picas/drumgizmo-kits-generator/commit/d42617b62dbc2b233535360ab09c89a1de72e9ce))

- Update README.md [skip ci]
  ([`5933ef6`](https://github.com/e-picas/drumgizmo-kits-generator/commit/5933ef6ae756e15279ffa3e8d64770308e61351c))

- Update README.md [skip ci]
  ([`4bd8aa5`](https://github.com/e-picas/drumgizmo-kits-generator/commit/4bd8aa52e9ceed28573332f795cf67218ab6bb55))

- Upgrade minimal Python version to 3.9
  ([`f436bf1`](https://github.com/e-picas/drumgizmo-kits-generator/commit/f436bf1d15176514284f2bcc4b90dcd344358a5e))

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

### Documentation

- Review the README [skip ci] ([#15](https://github.com/e-picas/drumgizmo-kits-generator/pull/15),
  [`86a475a`](https://github.com/e-picas/drumgizmo-kits-generator/commit/86a475afe96a9109e5d0d6155c4215f71a1ca403))

* docs: review the README [skip ci]

* docs: Update README.md [skip ci]

- Update README.md [skip ci]
  ([`97b7f9c`](https://github.com/e-picas/drumgizmo-kits-generator/commit/97b7f9c1eb86e027bdda9605ec9e634f427b6f5a))

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

### Documentation

- Review the README + new issues templates
  ([`1652261`](https://github.com/e-picas/drumgizmo-kits-generator/commit/1652261170eeb1f739507721d48674c93a05a44e))

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
