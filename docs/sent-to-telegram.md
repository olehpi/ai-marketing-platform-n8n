# Sent to Telegram Workflow

## Purpose

`workflow/Sent to Telegram.json` is a shared notification subworkflow. It sends an AI response to a Telegram user and sends formatted copies to the configured administrator and technical-support chats.

## Input Contract

| Field | Description |
| --- | --- |
| `output` | AI-generated response. |
| `inputMessage` | Original user message. |
| `sourceType` | One of `Telegram`, `Facebook`, or `GoogleSites`. |
| `user` | Display name of the requester. |
| `chatId` | Telegram chat ID for the client response. |
| `userName` | Reply target: a Telegram username, Facebook contact, or email address. |

## Routing and Formatting

1. The workflow removes any `<function>...</function>` blocks from `output`.
2. A switch routes the request by `sourceType`.
3. Source-specific formatter nodes create a client response and an internal message containing the source, user, original request, AI output, and reply target.
4. The client response is sent to `chatId`; formatted notifications are sent to the administrator and technical-support chats.

Messages use Telegram's HTML parse mode, with link attribution disabled.

## Configuration

1. Import `workflow/Sent to Telegram.json` into n8n.
2. Configure the Telegram credential in all three Telegram send nodes.
3. Replace the embedded administrator and technical-support chat IDs with deployment values.
4. Re-select this subworkflow in calling workflows after import.
5. Test all supported `sourceType` values before activation.

## Notes

- Unrecognised source types take the `Another` switch output, which has no connected formatter or delivery node.
- The workflow falls back to `Sorry, I couldn't find an answer for your request.` when no client output is available.
- Avoid sending unescaped user-controlled HTML because messages are delivered in HTML parse mode.
