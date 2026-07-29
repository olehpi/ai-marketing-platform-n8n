# Append Portfolio and Contacts Workflow

## Purpose

`workflow/Append Portfolio and Contacts workflow.json` conditionally appends portfolio and contact links to an AI response. It is used by the Google Sites assistant as a reusable subworkflow.

## Input

Call the workflow with:

```json
{
  "output": "AI-generated response",
  "senderId": "visitor-or-chat-identifier"
}
```

## Behavior

1. The workflow counts entries in `n8n_chat_histories` for the supplied `senderId`.
2. If the count is below `3`, it appends the configured portfolio and contact block to `output`.
3. If the count is `3` or greater, it returns `output` unchanged.

The returned item contains the final `output` field.

## Dependencies

- A PostgreSQL credential with access to the `n8n_chat_histories` table.
- The table must contain a `session_id` column used to match the caller's `senderId`.

## Configuration

1. Import `workflow/Append Portfolio and Contacts workflow.json`.
2. Configure the PostgreSQL credential in `Execute Row Count`.
3. Review the portfolio URL, social links, phone number, and email text in `Prepare Portfolio and Contacts Output`.
4. Adjust the threshold if a different contact-prompt frequency is required.

## Security

Use parameterized queries or validated identifiers if the workflow input can be supplied by untrusted callers. Keep database credentials in n8n credentials rather than workflow JSON or source control.
