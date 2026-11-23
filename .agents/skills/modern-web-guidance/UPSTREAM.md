# Upstream provenance

- Project: [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance).
- Recorded source revision: `64a6d708f5a43f2cd3fde5d4d7db3905ba1bdf65`.
- Recorded skill entry: `skills/modern-web-guidance/SKILL.md`.
- The installation metadata is retained in the repository-root `skills-lock.json`.
- [LICENSE](LICENSE) reproduces the upstream repository's Apache License 2.0 at that revision. No root `NOTICE` file was listed in the pinned repository tree.
- The existing skill entry and 210 Markdown guides are retained without content edits. `LICENSE` and this provenance note are local packaging additions.
- Existing trailing whitespace and final blank lines in upstream guides are preserved; whitespace checks for newly authored packaging are separate from those upstream formatting advisories.

Vendoring these documents does not install or execute a package. Upstream examples invoke `modern-web-guidance@latest`; the recorded Git revision does not pin that future npm execution. Review network access and package trust separately before running those commands. No credentials or workstation-specific skill registry belong in this directory.

The `SubtleCrypto.supports` examples in `guides/security/client-side-encryption.md` contain public WebCrypto algorithm identifiers. Two generic-API-key scan findings at lines 187 and 201 refer to those identifiers, not secret key material; keep this distinction explicit rather than disabling the scanner globally.
