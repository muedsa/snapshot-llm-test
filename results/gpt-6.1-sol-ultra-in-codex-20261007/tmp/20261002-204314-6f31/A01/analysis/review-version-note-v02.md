# Review correction

Use **calculated-review-v02.json**. Version01 computations for all amounts, totals, rates and the August conclusion were correct. Its two max-month validation fields were wrong because PowerShell Sort-Object by a named property did not evaluate the values in an OrderedDictionary. Version02 sorts via explicit dictionary-key expressions and verifies both maxima are September. Original script/JSON are retained to preserve the attempt.

The matching final review script is compute-review-v02.ps1. design-notes-v01.md remains valid except its referenced JSON filename should be interpreted as calculated-review-v02.json.
