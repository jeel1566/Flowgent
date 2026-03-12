# Flowgent Speaker Notes

## 01. What Flowgent is
Flowgent is a Chrome extension plus backend that helps people work with n8n using natural language. The important point is that it is not a separate dashboard product first; it sits next to the workflow canvas and assists the real work.

## 02. Why it exists
n8n is powerful, but it assumes users understand nodes, data flow, and workflow debugging. Flowgent reduces that learning curve and shortens the path from idea to working automation.

## 03. Where the user sees it
The side panel gives the user one home for chat, dashboard, and settings. That means the assistant stays close to the workflow instead of forcing tab switching.

## 04. Chat experience
A user can ask for a workflow, an edit, or an explanation in plain English. The extension sends that to the backend and displays the result in a simple conversational UI.

## 05. Agent protocol
The backend does not use one generic prompt path for every request. It classifies the job into Fast, Standard, or Deep mode, then researches templates and docs before building anything important.

## 06. Real workflow actions
This is not only a chatbot. The backend can search nodes, fetch templates, validate workflow JSON, create workflows, update workflows, and execute them.

## 07. Information Hand
When a user hovers over a node, Flowgent can inject a tooltip with context about that node. This reduces friction because documentation appears at the moment the user needs it.

## 08. Dashboard and execution view
The extension also gives users workflow visibility and execution history. It is trying to make Flowgent useful before build, during build, and after deployment.

## 09. Architecture choice
The extension talks to FastAPI, and the backend can use MCP or direct n8n API calls depending on the situation. That hybrid design is practical because it preserves flexibility when MCP is not enough.

## 10. Model and deployment flexibility
The code supports multiple model providers and is structured for deployment. That matters because teams may want different model costs, latency, or compliance tradeoffs.

## 11. Reliability and guardrails
The codebase shows effort around graceful errors, connection checks, caching, and API fallbacks. That is important because workflow tooling fails in real life if it only works in the happy path.

## 12. Closing message
The clean way to describe Flowgent is this: it is an AI n8n copilot that helps users understand, build, and operate workflows without leaving context.
