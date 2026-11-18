# `peoplecomfort serve`

Start the local workbench on the loopback address.

```console
peoplecomfort serve --port 8765
```

| Option | Meaning and default |
|---|---|
| `--port INTEGER` | Local TCP port; default 8765 |
| `-h`, `--help` | Show parser help |

Open `http://127.0.0.1:8765`, edit inputs or import a project, click Run comparison, and export the result ZIP. Changes invalidate the displayed run until recomputed. The interface checks request origin and binds only to `127.0.0.1`; it is not a hosted multi-user service. Stop with Ctrl+C. The current web interface exposes the bundled demo and scenario editor, while the CLI accepts any valid JSON within prototype limits.

Open `/framework` for the schema-v2 JSON workbench. The home page remains the original A3 example. Both call the same version-aware server endpoint and export the matching result format.
