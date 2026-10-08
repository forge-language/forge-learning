# Forge Learning

An eight-lesson introduction to Forge, with browser-compatible examples and a
terminal practice runner. English is the primary language; every lesson also
contains Korean explanations and challenges.

Start in the [browser playground](https://forge-lang.org/learn), or install
Forge and practice locally. The course progresses from a greeting to a small
ticket-total program. Try predicting each result before running it, then complete
the challenge without looking at `solutions.json`.

## Install and practice

Install the SDK using the [official installer guide](https://github.com/forge-language/forge-platform#install),
or build the [compiler and SDK from source](https://github.com/forge-language/forge#build-and-install).
Python 3 is required for the course runner. Node.js 18+ is needed only for the
JavaScript backend. Check that `forge --help` works before continuing.

```sh
git clone https://github.com/forge-language/forge-learning.git
cd forge-learning
python3 scripts/learn.py list
python3 scripts/learn.py show hello
python3 scripts/learn.py run hello
python3 scripts/learn.py run hello --backend js
```

Use `--forge /path/to/forge` before the subcommand when the installed compiler is
outside `PATH`. The runner does not build or download a toolchain.

Copy a lesson's source into your own `practice.fg`, change it, and run:

```sh
python3 scripts/learn.py run hello --file practice.fg
python3 scripts/learn.py run hello --file practice.fg --solution
```

The first command checks the original lesson output. The second checks the
challenge output. `--solution` without `--file` runs the reference challenge
answer; use that only after trying the exercise yourself. Output comparisons are
exact, including newlines. Each compile runs in a temporary directory; program
execution has a three-second limit and output is limited to 64 KiB. Commands use
argument arrays without a shell. Local Forge programs still execute native code;
this runner is a learning utility, not a security sandbox.

## Lessons

| ID | Topic | Challenge result |
| --- | --- | --- |
| `hello` | Entry point and printing | `Hello, learner!` |
| `variables` | Variables and arithmetic | `6` |
| `conditions` | `if` and `else` | `try again` |
| `loops` | `while` and accumulation | `15` |
| `functions` | Parameters and return values | `12`, then `21` |
| `strings` | Imports, concatenation, byte length | `Hello, Ada`, then `3` |
| `int64` | Exact large integers | `9007199254740993`, then `9007199254740995` |
| `mini-project` | Combining the earlier lessons | `20`, then `keep going` |

These examples use the supported native/JavaScript subset. Forge remains an
experimental compiler: complete type and ownership checking are not implemented.
The course avoids filesystem, network, platform FFI and concurrency APIs that a
browser cannot directly provide. `str_len` counts UTF-8 bytes; it is not a count
of human-perceived characters. The integer lesson stays within signed 64-bit
bounds and does not promise defined overflow behavior.

## Editor practice with LSP

Install a server from [language-server](https://github.com/forge-language/language-server)
and choose your editor client:

- [VS Code and Cursor](https://github.com/forge-language/vscode-extension)
- [Sublime Text Forge syntax](https://github.com/forge-language/sublime-syntax) and
  [LSP-Forge](https://github.com/forge-language/sublime-text)
- [Vim and Neovim](https://github.com/forge-language/editor-configs)

Open your saved `.fg` file to use completion and diagnostics while practicing.
The browser runs compiled JavaScript; local editor LSP and a local compiler are
separate tools. A working completion list does not prove complete type checking.

## Data and verification

`course.json` is the browser/terminal contract: `schema_version: 1` and an ordered
`lessons` array. Each lesson has a stable `id`, bilingual `title`, `summary`,
`explanation`, `challenge`, Forge `source`, and exact `expected_output`.
`solutions.json` stores reference challenge source/output separately.

```sh
python3 scripts/learn.py check
FORGE=/path/to/forge python3 -m unittest discover -s tests -v
```

The checker compiles and runs all eight lessons and eight challenge solutions in
both backends: 32 actual executions. CI builds the public compiler at immutable
commit `9b1d1a6c86a688ba56158bd5c014d836c151f289`; that compiler's dependency manifest
pins runtime `61cd2e54768ec9d1e9a4f727772cf1aae0eef778` and standard library
`f0b92f8846f4797fd057b2c8b415f6bdba87a699`. Tests additionally exercise compile
errors, an infinite loop, incorrect output, literal command arguments and output
limits. This validates these examples, not every language feature.

한국어 학습 안내는 [빠른 시작](docs/quickstart.ko.md)을 참고하세요. 터미널에서는
`python3 scripts/learn.py --language ko show hello`로 한국어 설명을 볼 수 있습니다.

Licensed under Apache-2.0.
