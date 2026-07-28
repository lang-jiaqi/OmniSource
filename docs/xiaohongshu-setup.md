# Xiaohongshu creator source (OpenCLI)

OmniSource can monitor explicitly configured Xiaohongshu creators through
[OpenCLI](https://github.com/jackwener/OpenCLI). OpenCLI reuses a logged-in
Chrome session through its Browser Bridge. OmniSource never stores account
cookies and never likes, comments on, or publishes content.

## Prerequisites

1. Install OpenCLI and its Chrome Browser Bridge extension.
2. Keep Chrome running and log in to `xiaohongshu.com`.
3. Verify the connection:

```bash
opencli doctor
opencli xiaohongshu user USER_ID --limit 3 -f json
```

On macOS, if `opencli doctor` returns `Unable to find application named
'OpenCLIApp'`, use the bundled runtime instead of the managed `opencli`
launcher:

```bash
env -u OPENCLI_DAEMON_PORT \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node \
  /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js \
  doctor
```

After it reports that the daemon and extension are connected, keep this
environment variable in the same terminal when running OmniSource:

```bash
export OPENCLI_COMMAND='env -u OPENCLI_DAEMON_PORT /Applications/OpenCLIApp.app/Contents/Resources/node_modules/node/bin/node /Applications/OpenCLIApp.app/Contents/Resources/node_modules/@jackwener/opencli/dist/src/main.js'
```

On Windows PowerShell, use the normal `opencli` command when `opencli doctor`
reports `Daemon: running` and `Extension: connected`. The macOS path above is
not portable.

OpenCLI is intended for a persistent desktop session. Do not run this source in
an ephemeral GitHub Actions runner. Run the collection locally and inspect the
Markdown report, or use another source when your fork needs fully automated
GitHub Actions runs.

## Configure a track

Copy the example:

```bash
cp examples/tracks/xiaohongshu-radar.yaml tracks/builder/my-xhs-radar.yaml
```

Set one or more exact creator IDs or profile URLs:

```yaml
sources:
  - xiaohongshu

xiaohongshu:
  enabled: true
  command: opencli
  timezone: Asia/Shanghai
  days: 1
  max_notes_per_creator: 20
  fetch_details: true
  creators:
    - name: "Creator name"
      user_id: "5d8f88dc0000000001005d3a"
    - name: "Another creator"
      profile_url: "https://www.xiaohongshu.com/user/profile/USER_ID"

output:
  top_social: 10
```

`days: 1` means the current calendar day in the configured timezone. Pinned old
posts are filtered using the timestamp encoded in the 24-character note ID.
When OpenCLI exposes a real timestamp in its output, that timestamp takes
precedence.

Run locally:

```bash
uv run omnisource run --track builder/my-xhs-radar
```

## Security and operational boundaries

- Signed URLs containing `xsec_token` are used for the immediate OpenCLI detail
  call and as report links because unsigned Xiaohongshu note URLs currently
  redirect to an error page. The per-note share signature therefore appears in
  published Markdown/HTML links and may eventually expire. OmniSource never
  writes it to logs, error messages, or `Signal.extra` metadata.
- If Chrome is logged out, OpenCLI is missing, or Xiaohongshu shows a security
  challenge, the source reports the failure and the other OmniSource sources
  continue normally.
- Use a dedicated Xiaohongshu account and keep request volume modest. Browser
  automation can trigger platform risk controls.
- The first implementation analyzes post text and engagement metadata. Image
  and video understanding are intentionally deferred.
