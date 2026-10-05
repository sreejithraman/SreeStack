# Feature recipe example


The values below illustrate the formula; replace them with discovered product
facts and available tooling, rather than copying commands into a project.

```markdown
# Export a report (`reports.export`)

## User-facing description
Users download a report containing the selected records.
Sub-features: export selected rows; recover from unavailable download storage.

## How to get to it
- `toolbar`: Open Reports, select rows, choose Export in the toolbar.
- `menu`: With Reports active, choose File → Export Selected.
Both reach the export dialog; verify selection transfer from each entry point.

## Driving it with the attached browser
Prerequisites: shared launch/account setup; disposable report with known rows;
an isolated download directory. Use the host-attached browser and its download
inspection tools. If those tools are unavailable, record the harness gap.

Workflow `selected-rows` (required assertions):
1. Enter through `toolbar`, then separately through `menu` from equivalent
   state. Expect the export dialog to contain the selected rows. Proof: dialog
   snapshot for each entry point.
2. Choose CSV and confirm. Expect exactly one download and a settled success
   state. Proof: download event and result snapshot.
3. Open the saved file through a fresh filesystem read. Expect the documented
   headers and exactly the selected rows. Proof: parsed values and file path.

Workflow `storage-error` (required assertions):
1. Use the supported disposable fixture for unavailable download storage.
   Confirm export. Expect an actionable error, no partial output, and the
   selection preserved. Proof: error state and fresh directory inspection.
Cleanup: remove only this run's disposable report and downloaded file after
copying redacted evidence outside the scratch directory.

## Gotchas
Wait for the download completion event; clicking Confirm is not completion.
Storage-error recipe is draft/blocked until a supported fixture is available.
```
