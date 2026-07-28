# Adding a publisher

A publisher takes the finished `Report` and delivers it somewhere — a file, an
issue, a chat message, or another external destination. Same shape as adding a source.

## 1. Write the publisher

Create `omnisource/publishers/yourthing.py`:

```python
from __future__ import annotations

from .base import Publisher, Report


class YourThingPublisher(Publisher):
    name = "yourthing"

    def publish(self, report: Report) -> None:
        # report.markdown   — the rendered briefing
        # report.sections   — {type: [Signal, ...]} if you want structured access
        # report.track      — the track config
        # report.date       — "YYYY-MM-DD"
        # report.reports_dir — where local outputs go
        ...
```

Degrade gracefully: if the destination isn't configured (no token, no URL),
print a skip message and return rather than raising — one publisher shouldn't
break the run. See [`github_issue.py`](../omnisource/publishers/github_issue.py).

## 2. Register it

In [`publishers/__init__.py`](../omnisource/publishers/__init__.py):

```python
from .yourthing import YourThingPublisher

PUBLISHER_REGISTRY = {
    ...,
    "yourthing": YourThingPublisher,
}
```

## 3. Use it

Add the name to a track's `publishers:` list (or to `DEFAULT_PUBLISHERS`). The
default is `["markdown", "github_issue"]`. The official website's Pages
publisher is private and is not part of the public DIY package.
