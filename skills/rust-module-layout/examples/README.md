# rust-module-layout — Examples

Copy-paste skeletons and worked refactorings for in-crate module layout.

## Files

| File | Contents |
|------|----------|
| [templates.md](templates.md) | Six layout templates (A: small, B: medium, C: large, D: lib+bin, E: multi-bin, F: plugin) with copy-paste skeletons |
| [visibility-decisions.md](visibility-decisions.md) | Seven worked examples of choosing `pub` / `pub(crate)` / `pub(super)` / `pub(in path)` / private |
| [splitting-files.md](splitting-files.md) | Step-by-step: split a 600-line file into a directory without breaking callers |
| [refactoring-anti-patterns.md](refactoring-anti-patterns.md) | Seven refactorings: flat lib.rs, monster file, leaky privacy, deep public tree, `#[macro_use]`, vague names, mixed layouts |

## Quick Navigation

- **I'm starting a new crate** → `templates.md` Template A or B
- **My lib.rs is unreadable** → `refactoring-anti-patterns.md` Refactor 1
- **One of my files is 500+ lines** → `splitting-files.md`
- **I'm not sure whether to make something `pub`** → `visibility-decisions.md`
- **Module names are vague** → `refactoring-anti-patterns.md` Refactor 6
- **I'm migrating from Java/Python** → `../references/coming-from-java-python.md`
