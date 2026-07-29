# Prices Tool

## Purpose

`workflow/Prices Tool.json` is a reusable subworkflow that exposes the current price list stored in Google Sheets to other n8n workflows and AI tools.

## Behavior

1. The workflow starts when another workflow executes it.
2. It reads all rows from the configured `video_(PL/EN/UA/...)` worksheet in the `Prices` spreadsheet.
3. The retrieved rows are returned to the calling workflow.

## Input and Output

The workflow accepts the caller's execution data and does not require specific input fields. Its output is the row data returned by Google Sheets, so callers should handle the sheet's current column structure.

## Configuration

1. Import `workflow/Prices Tool.json` into n8n.
2. Configure a Google Sheets service-account credential in `GetPricesFromTable`.
3. Select the price spreadsheet and the intended worksheet.
4. Share the spreadsheet with the service account if it is not already accessible.
5. Re-select this workflow in calling workflows or AI tool configurations after import.

## Operations

- Keep the worksheet schema stable or update callers when columns change.
- Treat spreadsheet sharing and service-account credentials as sensitive configuration.
- Verify the active sheet contains the current published prices before enabling dependent workflows.
