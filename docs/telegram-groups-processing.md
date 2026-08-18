# Processing Telegram Channels and Groups

This set of workflows automates Telegram lead collection and message processing for the AI marketing platform.

## Workflows

### `Collect Telegram Clients From Groups Agent`

- Runs on a schedule and reads target group names and limits from Google Sheets.
- Calls the Telegram bridge API to fetch recent messages from the configured groups.
- Normalizes chat and sender data, then stores the results back into Google Sheets.
- Uses `message_id` as the matching key to avoid duplicate rows.

### `Collect Telegram Contacts from Messages`

- Extracts contact data from incoming Telegram messages.
- Sends validation requests through the Telegram bridge API.
- Writes enriched contact records to Google Sheets for follow-up processing.

### `Telegram AI Sales & Ads Agent`

- Prepares outgoing sales and ads responses for Telegram leads.
- Pulls the target contact context from Google Sheets.
- Saves the final user-facing message and contact identifiers back into the sheet.

## Shared Behavior

- All workflows rely on the `TelegramClients` Google Sheet as the shared data source.
- The Telegram bridge service acts as the API layer between n8n and Telegram.
- Data is stored in Google Sheets for later sales, outreach, and analytics steps.

## Notes

- Replace spreadsheet IDs, sheet names, and API endpoints only if the deployment layout changes.
- Keep Telegram credentials and bridge access aligned across all three workflows.
