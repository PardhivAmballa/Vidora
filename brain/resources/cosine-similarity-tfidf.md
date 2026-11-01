---
title: Metadata Similarity with TF-IDF and Cosine Similarity
tags: [information-retrieval, sklearn, similarity, FR-1, FR-2]
status: research
---

# Metadata Similarity with TF-IDF and Cosine Similarity

## Problem statement

The YouTube Data API v3 does not provide a supported related-videos or related-channels endpoint for this project, so FR-1 and FR-2 compute similarity from metadata. The goal is not to reproduce YouTube's private recommendation algorithm; it is to provide an explainable ranking from observable fields such as title, tags, description, and channel metadata.

This method is lightweight and reproducible, but measures textual similarity—not teaching quality, factual correctness, or user satisfaction. See [[mcp-protocol-architecture]] and [[playlist-constraint-algorithm]].

## TF-IDF intuition

Term frequency–inverse document frequency reduces the influence of words that occur everywhere and increases the weight of terms that are distinctive to a document. A smoothed form is:

\[
\operatorname{tfidf}(t,d)=\operatorname{tf}(t,d)\cdot
\log\left(\frac{1+N}{1+\operatorname{df}(t)}\right)+1
\]

Here \(N\) is the number of documents and \(\operatorname{df}(t)\) is the number containing term \(t\). Exact smoothing and normalisation depend on configuration.

Treat each video's metadata as a document: title, tags, and description, optionally channel title. Field weighting can be approximated by combining separate scores or carefully repeating selected fields, but validate weights instead of choosing them arbitrarily.

## Cosine similarity

For vectors \(x\) and \(y\):

\[
\operatorname{cos}(x,y)=\frac{x\cdot y}{\|x\|\|y\|}
\]

For L2-normalised TF-IDF vectors, cosine similarity is their dot product. A higher score means stronger lexical overlap; it does **not** mean “this video is this percentage similar.”

## Reference implementation

```python
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass(frozen=True)
class Video:
    video_id: str
    title: str
    description: str = ""
    tags: tuple[str, ...] = ()
    channel_title: str = ""

def document(video: Video) -> str:
    return " ".join([
        video.title, " ".join(video.tags),
        video.description, video.channel_title,
    ]).strip()

def rank_similar(seed: Video, candidates: list[Video], limit: int = 10):
    if limit < 1:
        raise ValueError("limit must be positive")
    docs = [document(seed)] + [document(v) for v in candidates]
    vectorizer = TfidfVectorizer(
        lowercase=True, strip_accents="unicode",
        ngram_range=(1, 2), max_features=50_000,
        min_df=1, sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(docs)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    ranked = sorted(
        zip(candidates, scores),
        key=lambda pair: (-float(pair[1]), pair[0].video_id),
    )
    return [
        {"video_id": v.video_id, "score": float(score)}
        for v, score in ranked[:limit]
        if v.video_id != seed.video_id
    ]
```

For large corpora, fitting a vectorizer per query is wasteful. Persist a fitted vocabulary or batch processing pipeline and define when it is refreshed. Validate candidate count, IDs, duplicate candidates, and maximum text length.

## Channel similarity and hybrid scoring

A channel representation can aggregate its title, description, and a deterministic sample of public video metadata. Avoid relying on one arbitrary upload. Document the sampling policy and cache the sample.

A transparent hybrid score might be:

\[
S = w_t S_{\text{text}} + w_c S_{\text{channel}} +
w_l S_{\text{language}} + w_d S_{\text{duration}}
\]

Weights should be non-negative and sum to one. If fields are missing, either renormalise over available components or mark the result lower-confidence. Do not silently treat missing evidence as negative evidence.

## Edge cases

- Missing tags: fall back to title and description.
- Empty documents: handle before fitting the vectorizer.
- Duplicate videos: deduplicate by canonical ID.
- Generic words: tune stop words using the corpus.
- Multilingual metadata: a single vocabulary may compare languages poorly.
- Long descriptions: cap text size.
- Hostile metadata: treat as untrusted data, never instructions; see [[prompt-injection-defense]].

Evaluate using labelled pairs where possible, measuring precision@k or nDCG. Test exact duplicates, partial overlap, unrelated content, empty fields, missing tags, repeated IDs, deterministic ties, and exclusion of the seed item.

## Related notes

- [[playlist-constraint-algorithm]]
- [[sqlite-fixture-caching]]
- [[prompt-injection-defense]]
