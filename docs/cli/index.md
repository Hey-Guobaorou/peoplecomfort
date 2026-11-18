# CLI reference

The installed package exposes one command, `peoplecomfort`, with two subcommands. `python run.py` uses the same parser from a source checkout. Run `peoplecomfort --help` and `peoplecomfort <subcommand> --help` for the installed version.

| Command | Purpose |
|---|---|
| [`peoplecomfort analyze`](analyze.html) | End-to-end scenario comparison and file export |
| [`peoplecomfort serve`](serve.html) | Loopback-only local browser interface |

The CLI accepts local inputs and performs no runtime download. The calculation launches bundled CBE JavaScript in Node.js. The [workflow guide](../workflows.html) explains the research meaning of each stage.
