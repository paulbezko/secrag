# secrag, and the first time I didn't build alone

secrag is the project I point to when I think about the gap between reading how software is built and actually building it. On paper it was an app for asking questions of SEC filings — you pointed it at a company's annual report and it answered from the document itself. But that was never really why it stayed with me. It stayed with me because it was the first thing I made *with other people* instead of on my own, and almost everything I carried out of it came from that fact rather than from the idea.

## The problem we were trying to solve

A public company's annual report is a strange document. Everything you'd want to know is in there — how the business makes money, what it's worried about, what the numbers actually say — but it's a hundred-plus pages of careful, defensive prose written by people whose job is partly to not be too quotable. Reading one properly takes real time. Reading several to compare them takes more time than most people have.

The idea was simple to state: what if you could just ask. Point the thing at a company and a filing, ask "what are the main risks they flag this year" or "show me the cash flow statement," and get an answer that came from *that filing* rather than from whatever the model happened to remember. The model's general knowledge wasn't the point — its memory of a specific 10-K would be vague and possibly wrong. The point was to put the actual document in front of it at the moment of answering.

That's a retrieval problem before it's a language problem, and that distinction shaped the whole build.

## How it worked

Mechanically it came down to two halves: a pipeline that turned a filing into something searchable, and an agent that answered by reaching into what the pipeline had produced.

```
EDGAR        ──▶  PARSE +      ──▶  EMBED        ──▶  AGENT          ──▶  STREAMED
fetch filing      CHUNK             into FAISS        picks tools,        ANSWER
                  (text + XBRL)     vector store      retrieves           (websocket)
                                                          │
                                              ┌───────────┼───────────┐
                                       financial      semantic      google
                                       statements     filing text   search
                                       (XBRL)         (vectors)      (fallback)
```

The first part fetched filings from the SEC's EDGAR system and pulled them apart. Filings come in two flavours that matter here: there's the narrative text, and there's the structured financial data tagged in XBRL — the balance sheet, income statement, cash flow statement and so on, in a machine-readable form. We treated those differently, because they *are* different. You search prose by meaning; you retrieve a financial statement by name.

The narrative got chunked and embedded into a FAISS vector store so we could find the passages most relevant to a question by similarity rather than keyword. The structured financials were kept retrievable as whole statements.

Then the part I found most interesting: rather than a single retrieve-then-answer step, the answer came from an agent that could choose between tools. It had three. One pulled a named financial statement straight from the XBRL. One did semantic search over the filing text. One was a plain web search, used as sparingly as possible and only when the filing genuinely couldn't answer the question. The agent decided which to reach for, could use more than one, and built its answer from what came back. The reply streamed to the browser token by token over a websocket, so it felt like a conversation rather than a loading spinner.

`[SCREENSHOT: the chat answering a question about a specific filing, with the financial statement it pulled]`

## The decision that let two of us work at once

With more than one person building this, the most important decision wasn't a clever algorithm. It was where to draw the line down the middle so two people could work without constantly tripping over each other.

We split it cleanly into a Vue frontend and a Python backend that spoke to each other over a defined API, and treated that contract as the thing neither side broke without telling the other. The frontend knew nothing about how filings were parsed or how the agent chose its tools; the backend knew nothing about how the chat was rendered. As long as the shape of the messages between them held, we could each go deep on our own half.

For a while this felt obviously right, and mostly it was — it's the only reason two people could make progress in parallel at all. But the contract was also the thing that broke quietest. When one side changed what it sent and forgot to say so, nothing crashed; the other side just started behaving slightly wrong, and we'd lose an evening discovering that the disagreement was between us, not in the code. I came away believing the split was correct and that the real skill was in the communication around the seam, which is not a thing you can solve with architecture.

## It was a real thing, and that raised the stakes

This wasn't a notebook that ran on someone's laptop. There was a Postgres database behind Supabase holding the users, MongoDB keeping the chat histories, authentication with email verification and OAuth, a token-metered usage system, and Stripe wired up for actual paid tiers. It was deployed in a container on a real host, rebuilding and restarting itself off a webhook when we pushed. There was logging so we could see what was happening, and alerts so we'd hear about it when something went wrong.

Most of that isn't the interesting part of the idea. But building it taught me that the distance between "the demo works" and "other people can rely on this" is most of the work, and almost none of it is the part you brag about. A retrieval pipeline you can show a friend is a weekend. The accounts, the billing, the deployment, the not-falling-over — that's the months.

`[SCREENSHOT: the secrag dashboard / a filing being selected]`

## Why it isn't running now

The plain reason is that it was a project we were building to learn, alongside other commitments, and the momentum that carries something like that is finite. There was no dramatic failure. We got it working, we got it deployed, we learned an enormous amount, and then the cost of pushing it from "working" to "a product anyone could find and pay for" turned out to be a different and much larger kind of effort than the one we'd signed up for. At some point the honest thing was to call it what it was — the best apprenticeship either of us had had — and stop, rather than half-maintain it indefinitely.

`[FILL: if you want, a sentence here on the actual timeline and whether it had real users — only you know the true numbers, and the piece is stronger with one or two concrete ones, the way the HutHunters post used "fifty people" and "twelve months".]`

## What I'd change with hindsight

I only really understand most of these because we did the opposite first and lived with it.

We hardcoded secrets — API keys, a database password, signing secrets — straight into a config file that lived in the repository. They belonged in environment variables from the very first commit, kept out of version control entirely. It's the single most common beginner security mistake and we made it in the most ordinary way, by not thinking about it until later. Cleaning it up afterwards is genuinely annoying, because a secret that has ever been committed has to be treated as compromised forever, not just deleted going forward.

We caught errors too broadly. Bare `except` blocks are comforting because nothing blows up, but that comfort is the problem — they swallow the exact information you need when something is actually wrong, and turn a clear failure into a vague one. We never wrote a real test suite, only a folder of throwaway scripts we ran by hand, which is the one that stings most, because tests are how you find out you broke the API contract *before* your collaborator does, not after. And we vendored a whole library into the repo instead of pinning it as a dependency, which made the thing harder to read and harder to update for no real gain.

None of these are exotic. That's rather the point. The mistakes you make on a first serious project are almost all the boring, well-documented ones, and you make them anyway, because reading that you shouldn't do something is not the same as having watched it cost you.

## What it ended up being worth

If you score it the ordinary way, secrag is a failure: no revenue, nobody using it today, nothing left running. I've come to think that's simply the wrong scorecard for a first project like this one. What it gave me was the experience of building a real system end to end — retrieval, embeddings, an agent that reasons through tools, authentication, payments, deployment — and, more than any of that, the experience of building it *with* someone. How you split work so it can happen in parallel. How much of collaboration is communication around the parts where your code meets theirs. How to disagree about an approach and still ship. How to read someone else's half and trust it.

The truest thing I can say about it is a small one: it taught me what you only learn from other people, and it was worth every broken evening that took.

---

*Code, if you're curious: [secrag](LINK).*
