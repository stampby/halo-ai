# Contributing to halo-ai

Thanks for wanting to contribute. Here's how.

## Getting started

1. Fork the repo
2. Clone your fork
3. Create a branch: `git checkout -b my-feature`
4. Make your changes
5. Push: `git push origin my-feature`
6. Open a pull request

## What we need

- Bug reports with steps to reproduce
- Performance benchmarks on different hardware
- Documentation improvements
- New agent implementations
- Service integrations
- Testing on different AMD GPUs (gfx1100, gfx1101, gfx1151)

## Guidelines

- Keep it clean and simple
- Test your changes before submitting
- One PR per feature or fix
- No AI-generated spam PRs — we'll know
- Build from source, not prebuilt binaries
- Follow existing code style

## Agents

Want to build a new agent? Subclass `HaloAgent`, write a `check()` method, and submit a PR. Every agent is a Lego block.

## Security

Found a vulnerability? Do NOT open a public issue. Email the details privately. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree your work is licensed under Apache 2.0.

---

*stamped by the architect*
