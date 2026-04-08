.\.venv\Scripts\Activate.ps1
dq-pipeline --input "$PSScriptRoot\sample_data\customers.csv" --output "$PSScriptRoot\output\report.xlsx"
start "$PSScriptRoot\output\report.html"