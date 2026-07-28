# Adding a source

A source turns one external feed into `Signal`s. That's its whole job — no
filtering, ranking, or summarizing (the pipeline does that). Adding one touches
three places and nothing else.

## 1. Write the source

Create `omnisource/sources/yourthing.py`:

```python
from __future__ import annotations

from ..models import Signal
from .base import Source


class YourThingSource(Source):
    name = "yourthing"  # the key tracks will use

    def fetch(self, track: dict) -> list[Signal]:
        items = ...  # call the API / parse the feed
        return [
            Signal(
                id=...,                 # stable canonical id (used for dedup)
                title=...,
                url=...,
                type="paper",           # paper | repo | blog | release | benchmark
                published_at=...,       # tz-aware datetime, or None
                summary=...,
                authors=[...],
                sources=[self.name],
                code_url=...,           # optional
                popularity=...,         # optional int (upvotes/stars)
            )
            for item in items
        ]
```

Notes:
- Keep `id` canonical so the same item from two sources merges (e.g. the bare
  arXiv id, or `github:owner/repo`, or a post URL).
- Respect `track.get("days", 3)` for the time window.
- Raising is fine — `main.collect` isolates one source's failure from the rest.

## 2. Register it

In [`sources/__init__.py`](../omnisource/sources/__init__.py):

```python
from .yourthing import YourThingSource

SOURCE_REGISTRY = {
    ...,
    "yourthing": YourThingSource,
}
```

## 3. Use it

Add the name to a track's `sources:` list. Done — `main.py` doesn't change.

See [`sources/hf.py`](../omnisource/sources/hf.py) (API) and
[`sources/rss.py`](../omnisource/sources/rss.py) (feed parsing) for real examples.
