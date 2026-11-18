# `peoplecomfort analyze`

Run the complete calculation on one JSON project and write the result files.

```console
peoplecomfort analyze --project examples/minimal/project.json --out example-output
```

| Option | Meaning and default |
|---|---|
| `--project PATH` | Input JSON; default bundled `data/demo.json` |
| `--out PATH` | Output directory; default `results` relative to current directory |
| `--no-uncertainty` | Skip the joint stress grid; nominal comparisons still run |
| `-h`, `--help` | Show parser help |

The command prints selection JSON and the absolute output path. An invalid project, unavailable Node runtime or calculation error stops the command with an error. The output directory is created if needed and files with the same names are overwritten. See [stage 5](../workflow/output.html) for file meanings. If running from the source checkout without installation, prefix the command with `python run.py`.

The CLI dispatches by `schema_version`: v1 runs the original two-zone A3 workflow; v2 runs the general multi-zone framework. Use `examples/general/project.json` for direct multi-criterion scores or `examples/general-thermal/project.json` for three CBE-evaluated thermal zones. Output filenames differ between v1 and v2; inspect each run manifest.
