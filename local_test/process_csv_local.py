import pandas as pd
import json
from datetime import datetime


THRESHOLD_PERCENT = 5


def calculate_daily_metrics(file_path):
    df = pd.read_csv(file_path)

    df["cycle_time_seconds"] = pd.to_numeric(
        df["cycle_time_seconds"], errors="coerce"
    )

    invalid_rows = df[
        df["production_line"].isna() | df["cycle_time_seconds"].isna()
    ]

    df = df.dropna(subset=["production_line", "cycle_time_seconds"])

    metrics = {}

    for line, group in df.groupby("production_line"):
        metrics[line] = {
            "average_cycle_time": round(group["cycle_time_seconds"].mean(), 2),
            "completed_cycles": len(group)
        }

    return metrics, len(invalid_rows)


def compare_metrics(yesterday, today):
    result = []

    all_lines = sorted(set(yesterday.keys()) | set(today.keys()))

    for line in all_lines:
        yesterday_data = yesterday.get(line)
        today_data = today.get(line)

        if yesterday_data is None:
            result.append({
                "production_line": line,
                "yesterday_avg": None,
                "today_avg": today_data["average_cycle_time"],
                "change_percent": None,
                "status": "new_line"
            })
            continue

        if today_data is None:
            result.append({
                "production_line": line,
                "yesterday_avg": yesterday_data["average_cycle_time"],
                "today_avg": None,
                "change_percent": None,
                "status": "no_data_today"
            })
            continue

        yesterday_avg = yesterday_data["average_cycle_time"]
        today_avg = today_data["average_cycle_time"]

        change_percent = round(
            ((today_avg - yesterday_avg) / yesterday_avg) * 100,
            2
        )

        if change_percent > THRESHOLD_PERCENT:
            status = "worsened"
        elif change_percent < -THRESHOLD_PERCENT:
            status = "improved"
        else:
            status = "stable"

        result.append({
            "production_line": line,
            "yesterday_avg": yesterday_avg,
            "today_avg": today_avg,
            "change_percent": change_percent,
            "status": status,
            "completed_cycles_today": today_data["completed_cycles"]
        })

    return result


def generate_html(output, output_path):
    rows = ""

    for item in output["lines"]:
        rows += f"""
        <tr>
            <td>{item["production_line"]}</td>
            <td>{item["yesterday_avg"]}</td>
            <td>{item["today_avg"]}</td>
            <td>{item["change_percent"]}</td>
            <td>{item["status"]}</td>
            <td>{item.get("completed_cycles_today", "-")}</td>
        </tr>
        """

    html = f"""
    <html>
    <body>
        <h1>Daily Production Analytics Report</h1>

        <p>Generated at: {output["processed_at"]}</p>
        <p>Threshold: {THRESHOLD_PERCENT}%</p>
        <p>Invalid rows today: {output["invalid_rows_today"]}</p>

        <table border="1" cellpadding="8">
            <tr>
                <th>Production Line</th>
                <th>Yesterday Avg</th>
                <th>Today Avg</th>
                <th>Change %</th>
                <th>Status</th>
                <th>Completed Cycles Today</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    yesterday_file = "../data/production_data_2026-03-08.csv"
    today_file = "../data/production_data_2026-03-09.csv"

    output_html = "../reports/example_report.html"
    output_json = "../reports/result.json"

    yesterday_metrics, _ = calculate_daily_metrics(yesterday_file)
    today_metrics, invalid_rows_today = calculate_daily_metrics(today_file)

    comparison = compare_metrics(yesterday_metrics, today_metrics)

    output = {
        "processed_at": datetime.now().isoformat(),
        "threshold_percent": THRESHOLD_PERCENT,
        "invalid_rows_today": invalid_rows_today,
        "lines": comparison
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    generate_html(output, output_html)

    print("Processing complete!")