---
name: elephant-talk
description: Trigger whenever the user says anything about talking to elephants.
---


# Skill Instructions

When this skill is invoked, let me define these specific terms for you. When I refer to these terms I will enclose them in square brackets for clarity (e.g. [TRIGGER_REASON]):

SKILL INVOCATION CONTEXT
------------------------
TRIGGER_REASON: <describe why you called the skill>
TRIGGER_PROMPT: <If $ARGUMENTS is defined then use this, otherwise this is the exact prompt that triggered the skill, do not include any contextual information>
TRIGGER_CONTEXT: <**MUST BE 'NONE' UNLESS:** additional context that when combined with the TRIGGER_PROMPT, led to the invocation of this skill. This may include previous messages in the conversation, or any other relevant context that is not included in the TRIGGER_PROMPT but was still relevant to the decision to invoke this skill>
CONVERSATION_HISTORY: <**VERBATIM SNAPSHOT (DO NOT INTERPRET OR CHANGE)** of the full conversation history up until the point of invocation, including the TRIGGER_PROMPT. Prefix the user's conversation with 'User: ' and Claude's conversation with 'Claude: ' for clarity>

Next, print the following information:

The reason: [TRIGGER_REASON]
Prompt: [TRIGGER_PROMPT]
Context: [TRIGGER_CONTEXT]
Conversation History: [CONVERSATION_HISTORY]


Then continue with the task.

Show a large banner to the user that says "ELEPHANT TALK MODE ACTIVATED" and then followed by this line:
Elephant says $ARGUMENTS



