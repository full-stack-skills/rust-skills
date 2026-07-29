# Official UniFFI Documentation Map

Use this map to open the smallest relevant upstream page instead of loading the entire guide. The links were extracted from the official `latest` navigation and verified reachable on 2026-07-28. Because `latest` can change, record the UniFFI crate version and retrieval date in release-sensitive work.

## Overview and Tutorial

1. [UniFFI overview](https://mozilla.github.io/uniffi-rs/latest/index.html)
2. [Motivation](https://mozilla.github.io/uniffi-rs/latest/Motivation.html)
3. [Getting started](https://mozilla.github.io/uniffi-rs/latest/Getting_started.html)
4. [Prerequisites](https://mozilla.github.io/uniffi-rs/latest/tutorial/Prerequisites.html)
5. [Tutorial: describing the interface](https://mozilla.github.io/uniffi-rs/latest/tutorial/udl_file.html)
6. [Tutorial: Rust scaffolding](https://mozilla.github.io/uniffi-rs/latest/tutorial/Rust_scaffolding.html)
7. [Tutorial: foreign-language bindings](https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html)

## Type Model

8. [Namespace](https://mozilla.github.io/uniffi-rs/latest/types/namespace.html)
9. [Built-in types](https://mozilla.github.io/uniffi-rs/latest/types/builtin_types.html)
10. [Enumerations](https://mozilla.github.io/uniffi-rs/latest/types/enumerations.html)
11. [Records](https://mozilla.github.io/uniffi-rs/latest/types/records.html)
12. [Byte buffers](https://mozilla.github.io/uniffi-rs/latest/types/bytes.html)
13. [Functions](https://mozilla.github.io/uniffi-rs/latest/types/functions.html)
14. [Throwing errors](https://mozilla.github.io/uniffi-rs/latest/types/errors.html)
15. [Interfaces, Objects, and Traits](https://mozilla.github.io/uniffi-rs/latest/types/interfaces.html)
16. [Callback interfaces](https://mozilla.github.io/uniffi-rs/latest/types/callback_interfaces.html)
17. [Remote and External types](https://mozilla.github.io/uniffi-rs/latest/types/remote_ext_types.html)
18. [Custom types](https://mozilla.github.io/uniffi-rs/latest/types/custom_types.html)
19. [Default values](https://mozilla.github.io/uniffi-rs/latest/types/defaults.html)
20. [Exposing standard Rust traits](https://mozilla.github.io/uniffi-rs/latest/types/uniffi_traits.html)

## Interface Description and UDL

21. [Describing the interface](https://mozilla.github.io/uniffi-rs/latest/describing.html)
22. [The UDL file](https://mozilla.github.io/uniffi-rs/latest/udl/index.html)
23. [Enums in UDL](https://mozilla.github.io/uniffi-rs/latest/udl/enumerations.html)
24. [Errors in UDL](https://mozilla.github.io/uniffi-rs/latest/udl/errors.html)
25. [Functions in UDL](https://mozilla.github.io/uniffi-rs/latest/udl/functions.html)
26. [Interfaces in UDL](https://mozilla.github.io/uniffi-rs/latest/udl/interfaces.html)
27. [Records in UDL](https://mozilla.github.io/uniffi-rs/latest/udl/records.html)
28. [Types defined outside a UDL](https://mozilla.github.io/uniffi-rs/latest/udl/external_types.html)
29. [UDL docstrings](https://mozilla.github.io/uniffi-rs/latest/udl/docstrings.html)

## Procedural Macros

30. [Procedural Macros: Attributes and Derives](https://mozilla.github.io/uniffi-rs/latest/proc_macro/index.html)
31. [Proc-macro enumerations](https://mozilla.github.io/uniffi-rs/latest/proc_macro/enumerations.html)
32. [The `uniffi::Error` derive](https://mozilla.github.io/uniffi-rs/latest/proc_macro/errors.html)
33. [Functions, Constructors, and Methods](https://mozilla.github.io/uniffi-rs/latest/proc_macro/functions.html)
34. [The `uniffi::Object` derive](https://mozilla.github.io/uniffi-rs/latest/proc_macro/interfaces.html)
35. [The `uniffi::Record` derive](https://mozilla.github.io/uniffi-rs/latest/proc_macro/records.html)
36. [Traits](https://mozilla.github.io/uniffi-rs/latest/proc_macro/traits.html)
37. [Renaming via proc macros](https://mozilla.github.io/uniffi-rs/latest/proc_macro/renaming.html)
38. [Proc-macro docstrings](https://mozilla.github.io/uniffi-rs/latest/proc_macro/docstrings.html)
39. [Renaming and excluding items](https://mozilla.github.io/uniffi-rs/latest/renaming.html)

## Async and Binding Generation

40. [Async/Future support](https://mozilla.github.io/uniffi-rs/latest/futures.html)
41. [Generating bindings](https://mozilla.github.io/uniffi-rs/latest/bindings.html)
42. [Customizing binding generation](https://mozilla.github.io/uniffi-rs/latest/configuration.html)
43. [Foreign traits](https://mozilla.github.io/uniffi-rs/latest/foreign_traits.html)

## Kotlin

44. [Kotlin configuration](https://mozilla.github.io/uniffi-rs/latest/kotlin/configuration.html)
45. [Integrating with Gradle](https://mozilla.github.io/uniffi-rs/latest/kotlin/gradle.html)
46. [Kotlin lifetimes](https://mozilla.github.io/uniffi-rs/latest/kotlin/lifetimes.html)

## Swift

47. [Swift bindings](https://mozilla.github.io/uniffi-rs/latest/swift/overview.html)
48. [uniffi-bindgen-swift](https://mozilla.github.io/uniffi-rs/latest/swift/uniffi-bindgen-swift.html)
49. [Swift configuration](https://mozilla.github.io/uniffi-rs/latest/swift/configuration.html)
50. [Compiling a Swift module](https://mozilla.github.io/uniffi-rs/latest/swift/module.html)
51. [Integrating with Xcode](https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html)

## Python, Ruby, and WASM

52. [Python](https://mozilla.github.io/uniffi-rs/latest/python/configuration.html)
53. [Ruby](https://mozilla.github.io/uniffi-rs/latest/ruby/configuration.html)
54. [WASM](https://mozilla.github.io/uniffi-rs/latest/wasm/configuration.html)

## Internals

55. [Design Principles](https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html)
56. [Navigating the code](https://mozilla.github.io/uniffi-rs/latest/internals/crates.html)
57. [UniFFI Glossary](https://mozilla.github.io/uniffi-rs/latest/glossary.html)
58. [Lifting, Lowering, and Serialization](https://mozilla.github.io/uniffi-rs/latest/internals/lifting_and_lowering.html)
59. [Ffi converter traits](https://mozilla.github.io/uniffi-rs/latest/internals/ffi_converter_traits.html)
60. [Foreign to Rust calls](https://mozilla.github.io/uniffi-rs/latest/internals/rust_calls.html)
61. [Rust to Foreign calls](https://mozilla.github.io/uniffi-rs/latest/internals/foreign_calls.html)
62. [Managing Object References](https://mozilla.github.io/uniffi-rs/latest/internals/object_references.html)
63. [UniFFI Async Overview](https://mozilla.github.io/uniffi-rs/latest/internals/async-overview.html)
64. [UniFFI Async FFI details](https://mozilla.github.io/uniffi-rs/latest/internals/async-ffi.html)
65. [Rendering Foreign Bindings](https://mozilla.github.io/uniffi-rs/latest/internals/rendering_foreign_bindings.html)
66. [The UniFFI Bindings IR](https://mozilla.github.io/uniffi-rs/latest/internals/bindings_ir.html)
67. [Bindings IR Pipeline](https://mozilla.github.io/uniffi-rs/latest/internals/bindings_ir_pipeline.html)

## Upgrade Guide

68. [Upgrading v0.28.x to v0.29.x](https://mozilla.github.io/uniffi-rs/latest/Upgrading.html)

## Additional Primary Sources

- [mozilla/uniffi-rs](https://github.com/mozilla/uniffi-rs)
- [UniFFI changelog](https://github.com/mozilla/uniffi-rs/blob/main/CHANGELOG.md)
- [uniffi on crates.io](https://crates.io/crates/uniffi)
- [uniffi API documentation](https://docs.rs/uniffi/)
