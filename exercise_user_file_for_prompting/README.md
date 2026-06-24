# User File Prompting Exercise

This exercise shows how a small user preference file can change the shape of an
AI coding answer. You will run the same prompt twice: once with no extra context
and once with a `user.md` file that describes your preferences.

## Prompt

```text
write me code to prepare an N-qubit GHZ state and explain what you prepared briefly
```

## Steps

1. Run the prompt with no config files.

   Open a fresh chat with no project context. Run the prompt above and save the
   output.

2. Create a `user.md` file.

   Fill out `user.md` with your preferences for code library, programming
   language, response format, response depth, tone, and anything else that would
   make the assistant's answer more useful to you.

3. Run the same prompt in a new chat window with the `user.md` file uploaded.

   Save the new output and compare it with the first answer.

4. Consider personal use cases.

   Where could one or more user files help reinforce your preferences when using
   AI?

## Files

- `user.md`: Template for writing coding assistant preferences.
