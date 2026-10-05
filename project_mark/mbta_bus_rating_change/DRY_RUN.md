# Dry run record

Date: 2026-10-05. A fresh analyst agent (the strongest model available in this session, with code execution and
34 tool calls over about nine minutes) was given only prompt.md and an isolated copy of inputs/. It had no access
to the golden files or the design note.

Result: it reproduced the golden set in full. Net +149 (12,893 to 13,042), Route 65 +45, Route 465 +32,
supplemental 137 and 138, Route 65 span 05:58 to 21:03 and 05:00 to 25:33, flip point 14, and it reproduced both
office figures exactly (Finance +321 from the no school 24 August weekday, Planning +121 from multi route listings).
It used dates rather than rating labels, excluded rail replacement routes by route_desc, and counted each trip once.

Reading: the task is deterministic and the golden set is correct, which this run confirms. It did not stump the
strongest tool using model. The platform measures weaker models, where the trap record (rows versus trips,
rating label versus date, first weekday of the feed, offered figures) is expected to bite. After this run the
register and memo gained a second hard dimension, scheduled weekday revenue time per route, which adds the
stop_times join, times past 24:00, and 152 more checkable cells.

If the platform rollouts score at or above 50 percent, the next hardening step is to move the counting
convention out of the prompt and into a Board document in the package, so the model must find and apply it.
