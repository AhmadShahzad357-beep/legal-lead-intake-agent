<div align="center">

# Legal Lead Intake Agent

An autonomous AI agent that captures, qualifies, and responds to law firm leads in real time.

</div>

## Overview

The Legal Lead Intake Agent is a true tool-calling AI agent built for personal injury and family law firms. When a new lead arrives — from a website form, a tracked phone call, or a Google Local Services Ad — the agent reads the lead's message, decides how to classify it, and autonomously calls the tools it needs (CRM logging, team notification, and prospect auto-reply) in whatever order the situation requires.

Unlike a traditional automation script, no part of this system follows a fixed, hardcoded sequence. The language model is given a set of tools and decides — on every single lead — which ones to call, in what order, and with what data.

## Problem & Our Solution

**The problem:** Law firms lose high-value leads every day simply because of response speed. Prospects contacting multiple firms at once typically sign with whichever firm replies first. Manual intake also means inconsistent CRM data, missed high-urgency cases, and intake staff finding out about a new lead minutes or hours after it arrived.

**Our solution:** An always-on agent that:

- Reads and understands a lead's message the moment it arrives
- Classifies the practice area and extracts key case facts automatically
- Logs a clean, structured contact record to the CRM without exception
- Alerts the intake team instantly for urgent cases
- Sends a reassuring first reply to the prospect within seconds, before they contact a competing firm

## Key Features & What Makes This Different

| Feature | Description |
|---|---|
| Genuine agentic architecture | The LLM is handed real callable tools and decides the execution path itself — nothing is pre-scripted |
| Multi-channel intake | Normalizes payloads from website forms, CallRail transcripts, and LSA notifications into one pipeline |
| CRM auto-attribution | Maps UTM parameters and Google Click ID (GCLID) directly onto the created contact |
| Urgency-aware alerts | High-priority cases (e.g. active injury, time-sensitive filings) are flagged and pushed to the team immediately |
| Compliant auto-reply | Prospect messaging uses a Meta-approved template — the LLM decides whether to send, but never rewrites the approved wording |
| Live operations dashboard | A real-time command center shows every lead, its classification, and the status of every downstream action |
| Fault-tolerant by design | A failure in one tool (e.g. CRM downtime) never blocks the others — each action is logged and reported independently |

## System Architecture

<p align="center">
  <img src="docs/architecture.svg" alt="System architecture diagram of the Legal Lead Intake Agent" width="100%">
</p>

## Conclusion

The Legal Lead Intake Agent replaces a slow, manual, and inconsistent intake process with a single autonomous agent that reads, reasons, and acts on every lead the moment it arrives. By putting real decision-making in the hands of the LLM rather than a rigid script, the system adapts naturally to incomplete leads, unusual case types, and edge cases that a fixed workflow would mishandle — while still logging every action for full visibility on the operations dashboard.