# Citations: Meaning and Best Practices for AI

## What is a citation?

A **citation** is a reference that shows where a statement, fact, quotation, number, or idea came from.

A citation helps the reader:

- verify the information;
- find the original source;
- distinguish sourced facts from interpretation;
- evaluate the quality and authority of the evidence.

A useful mental model is:

```text
Claim -> Citation -> Original source
```

For example:

> AWS IAM roles use trust policies to define which principals can assume the role. [AWS Documentation]

In this example, **AWS Documentation** is the source and the reference pointing to it is the citation.

## Citation vs. source

A **source** is the original material containing the information, such as:

- official documentation;
- a standard;
- a research paper;
- a book;
- a government publication;
- a vendor specification;
- an article.

A **citation** is the pointer from your text to that source.

Example:

> `iam:PassRole` controls whether an identity can pass an IAM role to an AWS service. **[1]**

Here, `[1]` is the citation. The corresponding AWS IAM documentation is the source.

## Why citations matter when using AI

AI can summarize, combine, and explain information quickly, but the AI response itself should usually not be treated as the authoritative source for factual claims.

For research and technical work, prefer:

```text
Original source
      ↓
AI reads and analyzes it
      ↓
AI produces a claim or summary
      ↓
Citation points back to the original source
```

Avoid:

```text
AI produces a claim
      ↓
"AI said it"
```

Citations provide **grounding**: they connect generated conclusions to evidence that a human can inspect.

## Best practices

### 1. Prefer primary sources

Use the most authoritative original source available.

Prefer:

- official product documentation;
- standards and RFCs;
- research papers;
- government publications;
- official specifications;
- vendor documentation.

Use blogs, forum posts, Reddit, Stack Overflow, and other secondary sources mainly for experience, interpretation, examples, or community opinion.

### 2. Cite the original source, not the AI

If an AI summarizes AWS documentation, cite the AWS documentation.

If an AI summarizes a research paper, cite the paper.

The AI may be part of the workflow, but the supporting evidence should point to the underlying source.

### 3. Put citations close to the claims they support

Prefer:

> The service supports feature X. [1]

over placing a large unspecific list of sources at the end of a long document.

Close citations make it easier to determine exactly which source supports which statement.

### 4. Verify AI-generated citations

Never assume that an AI-generated citation is valid.

Check that:

- the source actually exists;
- the URL is correct;
- the author and title are correct;
- the cited section supports the claim;
- the version is appropriate;
- the publication date is correct.

AI systems can occasionally generate plausible-looking but incorrect references.

### 5. Include version and date when they matter

Technical information often changes.

Prefer:

> According to the .NET 10 documentation...

rather than:

> According to the .NET documentation...

Relevant context may include:

- software version;
- API version;
- cloud service version;
- standard revision;
- publication date;
- documentation access date.

### 6. Do not overload one citation

A citation should support the claim immediately associated with it.

Avoid attaching one citation to a paragraph containing several unrelated technical claims unless that source actually supports all of them.

### 7. Prefer stable links

Prefer stable documentation and canonical URLs over:

- search-result pages;
- temporary links;
- copied snippets;
- AI-generated summaries of the source.

### 8. Treat quotations carefully

For direct quotations:

- preserve the original wording;
- clearly mark the text as a quotation;
- identify the exact source;
- include page, section, heading, or line information when available.

### 9. Separate facts from inference

AI-generated research should distinguish between:

- **documented fact** — explicitly stated by a source;
- **inference** — derived from several facts;
- **recommendation** — suggested course of action;
- **opinion** — subjective interpretation.

Example:

> AWS documentation states X. [1]  
> Based on X and Y, this architecture would likely require Z.

The second sentence is analysis, not something that should be presented as if AWS explicitly stated it.

## Recommended citation pattern for AI-assisted research

For technical and professional work, a strong default is:

```text
Statement or claim. [citation]

Another statement. [citation]

Interpretation based on the cited evidence.
```

Then optionally include a short source list at the end.

This gives two useful layers:

1. **inline citations** for immediate verification;
2. **source list** for navigation and reference management.

## Prompt pattern for AI research

A reusable prompt:

```text
Research this topic using authoritative sources.

Requirements:
- Prefer primary sources and official documentation.
- Add a citation immediately after each important factual claim.
- Do not invent citations.
- Verify that each cited source supports the associated claim.
- Include publication, documentation, or version dates when relevant.
- Distinguish documented facts from your own inference.
- If a claim cannot be verified, explicitly say so.
```

## Prompt pattern for technical research

For software, cloud infrastructure, architecture, APIs, and similar topics:

```text
Use official documentation as the primary source.

For every important technical claim:
- provide the exact supporting citation;
- prefer the current documentation for the relevant version;
- distinguish documented behavior from inference;
- include version information where behavior can differ by release.

Do not treat blogs, forums, or AI-generated content as authoritative when official documentation is available.
```

## Practical verification workflow

A reliable AI-assisted workflow is:

```text
Question
   ↓
AI searches authoritative sources
   ↓
AI extracts relevant evidence
   ↓
AI creates an answer
   ↓
Claims receive citations
   ↓
Human or AI verifies citation -> claim alignment
   ↓
Final result
```

The most important verification step is not simply checking that a citation exists. It is checking that **the cited source actually supports the specific claim**.

## Summary

Good citation practice for AI can be reduced to five rules:

1. Prefer primary, authoritative sources.
2. Cite the original source rather than the AI.
3. Place citations close to the claims they support.
4. Verify every important AI-generated citation.
5. Clearly distinguish sourced facts from inference and recommendations.

The goal of citations is not merely to make an AI answer look more credible. The goal is to make the answer **traceable, reviewable, and verifiable**.