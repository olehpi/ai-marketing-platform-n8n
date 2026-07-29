# Google Sites AI Assistant

## Purpose

`workflow/Google Sites AI-assistent.json` processes contact-form submissions collected in a Google Sheet. It generates an AI response, sends the response and internal notifications, emails the visitor, and records completion in the sheet.

## Workflow

1. A schedule trigger runs every 10 minutes.
2. The workflow reads the first Google Sheets row whose `Status` is empty.
3. It maps `Message` to `text` and retains the visitor's `Email` and `Name`.
4. It treats the email address as `senderId`, detects the phrase `delete my data`, and calls `Agent workflow`.
5. The AI output is passed to `Append Portfolio and Contacts workflow`.
6. The enriched output is sent to `Sent to Telegram`, emailed to the visitor, and written back to the row's `Status` column.

## Dependencies

- `Agent workflow` must be imported and active.
- `Append Portfolio and Contacts workflow` must be imported and active.
- `Sent to Telegram` must be imported and active.
- A Google Sheets service-account credential must be configured for the messages spreadsheet.
- An SMTP credential must be configured for the email node.

## Google Sheet Contract

| Column | Use |
| --- | --- |
| `Date` | Included in the email context. |
| `Name` | Visitor name for the email and notifications. |
| `Email` | Recipient email address and AI conversation identifier. |
| `Message` | Visitor request passed to the AI agent. |
| `Status` | Empty rows are processed; the workflow saves the final response here. |
| `row_number` | Used to update the processed row. |

## Configuration

1. Import `workflow/Google Sites AI-assistent.json` into n8n.
2. Select the correct Google Sheets service-account credential in both Google Sheets nodes.
3. Set the target spreadsheet and worksheet in the read and update nodes.
4. Configure the sender address and SMTP credential in `Send an Email`.
5. Re-select the referenced subworkflows after import if n8n does not preserve their workflow IDs.
6. Replace embedded contact details and recipient settings with deployment values before activation.

## Data Deletion Requests

The classifier sets `isDeleteRequest` to `true` when the submitted message contains `delete my data` (case-insensitive). The flag is supplied to `Agent workflow`; implement the required retention or deletion action in that workflow and in your operational procedures.

## Operations

- Activate the workflow only after its three referenced subworkflows are available.
- Monitor failed executions for Google Sheets, SMTP, or downstream workflow errors.
- Do not store service-account keys, SMTP passwords, or personal data in the repository.
