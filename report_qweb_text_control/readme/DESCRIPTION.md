Allow text reports to generate positional text files by providing
precise control over whitespace, special characters, and field
formatting.

## Use Case

Generate fixed-width text files for legacy systems, bank transfers, or
any interface requiring exact positional formatting with specific
characters and spacing.

## Example

Template:

    <span t-esc="A(partner.name, 20)"/>
    <span t-esc="N(partner.id, 10)"/>
    <span t-esc="M(partner.partner_latitude, 12)"/>

Output:

    John Doe            00000012340000004158+

## Differences with `report_csv`

Both modules produce text reports for external systems, but they solve
different problems:

| | `report_csv` | `report_qweb_text_control` |
|---|---|---|
| Output | CSV (delimited, quoted) | Fixed-width positional text |
| Layout | Rows and columns defined in Python | QWeb template with formatter functions |
| Control | Standard CSV semantics | Exact spacing, padding, signs, control characters |
| Encoding | Configurable on the report | UTF-8 text |

Use `report_csv` when the target system parses delimited files.
Use this module when the layout must be positional and every character
counts, such as legacy fixed-width or banking interfaces.
