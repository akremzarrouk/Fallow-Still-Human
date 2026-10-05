Never stop processes by name or broad filters; only by the exact process ID you started.


## Prototype (Prototypes/llm-morning)
- Never call the Gemini API or run a morning unless the prompt's MODE is run.
  The free quota is 500 requests a day.
- v1/ to v4/ (and later frozen versions) are frozen copies. Never edit them.
- Prototype reports go in Prototypes/llm-morning/reports/.

## Investigations
- Read-only. Cite path:line. Write NOT FOUND when something does not exist.
  No opinions.
- Every deliverable includes the commands run and their output.

## Judging changes
- Judge every change by what a real family would do in this situation,
  not by whether a number moves. A metric is a clue, never the goal.
- Before proposing a mechanism, argue against it first: would a real
  person do this, and for what reason?

## North Star principles
- The code owns the truth: what happened, who perceived it, every
  number. The AI owns judgment and words. The AI never owns state.
- The code draws conclusions from what people perceive; the AI decides
  what they do about it.
- A line that describes an act makes the small model do that act. State
  situations; leave the choice open.
- Mechanisms may be unhuman; the output must read as human.
