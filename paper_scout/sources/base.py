from abc import ABC, abstractmethod

from paper_scout.utils.models import Paper


class PaperSource(ABC):
    """Common interface every paper source fetcher must implement."""

    name: str  # set by subclasses, matches SourceName enum value

    @abstractmethod
    def search(self, query: str, max_results: int) -> list[Paper]:
        """
        Search this source for papers matching `query`.
        Must return a list of populated Paper objects.
        Should not raise on empty results — return [] instead.
        Should catch and log network/API errors, returning [] rather than crashing the pipeline.
        """
        raise NotImplementedError