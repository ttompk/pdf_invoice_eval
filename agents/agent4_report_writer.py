def generate_report(discrepancies):
    report = "Discrepancy Report:\n"
    for d in discrepancies:
        report += f"Company: {d[0]}, Extracted: {d[1]}, Expected: {d[2]}\n"
    return report
