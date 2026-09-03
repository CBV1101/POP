# POP

**Primitives, Opportunities, Priorities.**

POP is a local product-management workspace. It helps you decide *what the smallest useful thing to build is*, *which customer problems actually matter*, and *what the team should work on next* — without collapsing evidence into a vague summary.

It runs in the browser from a small Python server. Paste interviews and tickets, import a backlog, or load a sample.

## What it does

### Primitives

Customers ask for features. POP looks for the **smallest shared build** that could cover the pile, instead of treating every ask as its own project.

Example: Terraform, a setup wizard, a permissions catalog, and docs might all be asking for one thing — a validated configuration spec — while something like dark mode stays uncovered.

Import open items from Linear, GitHub Issues, or Jira, or paste asks yourself.

### Opportunities

Paste messy feedback — interviews, tickets, reviews, notes. POP clusters related signals, separates **problems** from **requested solutions**, and ranks opportunities with **source quotes still attached**. Claims stay tied to what customers said.

### Priorities

Score the backlog and get a schedule, not just a sorted list.

- How loaded the team is (**capacity %**)
- How much of the team each item takes (**takes %**) and how long it takes (**effort in days**)
- **RICE** (reach, impact, confidence, effort)
- Revenue, ROI, go/no-go deals, churn if skipped, tech debt
- Must-dos: keep-the-lights-on, security patches, reliability, legal/compliance

Must-dos and high-priority work start first. Leftover team capacity can run **in parallel** with smaller items that finish no later than the main one. Output is ranked waves: what to start now, what runs together, and what waits.

## Run locally

Python 3.9+ (standard library only — no npm).

```bash
python3 server.py
```

Open [http://127.0.0.1:3335](http://127.0.0.1:3335)

Each workspace has a **Load sample** button if you want to see it before using your own data.

Backlog import uses your API token once for that request. Tokens are not stored on the server.

## Host a public URL (Render)

So other people can open POP in their browser:

1. Push this repo to GitHub (already at [CBV1101/POP](https://github.com/CBV1101/POP)).
2. Sign up at [render.com](https://render.com) and connect GitHub.
3. **New → Blueprint** and select the `POP` repo (uses `render.yaml`), **or** **New → Web Service** with:
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `python server.py`
   - Instance: Free
4. After deploy, Render gives you a URL like `https://pop-xxxx.onrender.com` — share that.

Free instances sleep after idle time; the first visit after sleep can take ~30 seconds.
