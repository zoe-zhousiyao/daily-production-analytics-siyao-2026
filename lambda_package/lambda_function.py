import csv
import json
import boto3
from io import StringIO
from datetime import datetime

s3 = boto3.client("s3")


def lambda_handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    if not key.startswith("incoming/") or not key.endswith(".csv"):
        return {"statusCode": 200, "body": "Ignored"}

    response = s3.get_object(Bucket=bucket, Key=key)
    csv_content = response["Body"].read().decode("utf-8")

    reader = csv.DictReader(StringIO(csv_content))

    line_values = {}
    invalid_rows = 0

    for row in reader:
        line = row.get("production_line")
        cycle_time = row.get("cycle_time_seconds")

        try:
            cycle_time = float(cycle_time)
        except (TypeError, ValueError):
            invalid_rows += 1
            continue

        if not line:
            invalid_rows += 1
            continue

        line_values.setdefault(line, []).append(cycle_time)

    results = []

    for line, values in line_values.items():
        avg = round(sum(values) / len(values), 2)

        baseline = 40  

        if avg > baseline * 1.1:
            status = "worsened"
        elif avg < baseline * 0.9:
            status = "improved"
        else:
            status = "stable"

        results.append({
            "production_line": line,
            "average_cycle_time_seconds": avg,
            "completed_cycles": len(values),
            "status": status
        })
    

    output = {
        "source_file": key,
        "processed_at": datetime.utcnow().isoformat(),
        "invalid_rows": invalid_rows,
        "lines": results
    }

    output_key = key.replace("incoming/", "processed/").replace(".csv", ".json")
    report_key = key.replace("incoming/", "reports/").replace(".csv", ".html")

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(output, indent=2),
        ContentType="application/json"
    )

    html_report = generate_html_report(output)

    s3.put_object(
        Bucket=bucket,
        Key=report_key,
        Body=html_report,
        ContentType="text/html"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "result_file": output_key,
            "report_file": report_key
        })
    }


def generate_html_report(output):
    rows = ""

    for item in output["lines"]:
        rows += f"""
        <tr>
            <td>{item["production_line"]}</td>
            <td>{item["average_cycle_time_seconds"]}</td>
            <td>{item["completed_cycles"]}</td>
            <td>{item["status"]}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily Production Analytics</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f7f7f7;
            }}
            .card {{
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                max-width: 900px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f0f0f0;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Daily Production Analytics Report</h1>
            <p><strong>Source file:</strong> {output["source_file"]}</p>
            <p><strong>Processed at:</strong> {output["processed_at"]}</p>
            <p><strong>Invalid rows:</strong> {output["invalid_rows"]}</p>

            <table>
                <tr>
                    <th>Production Line</th>
                    <th>Average Cycle Time (seconds)</th>
                    <th>Completed Cycles</th>
                    <th>Status</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """

    return html