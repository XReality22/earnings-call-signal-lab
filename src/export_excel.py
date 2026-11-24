"""Step 8: build the Excel summary workbook recruiters can open in 10 seconds."""
import pandas as pd
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, PatternFill
from config import OUT_DIR

def run():
    res = pd.read_csv(OUT_DIR / "results.csv")
    ev = pd.read_csv(OUT_DIR / "event_dataset.csv")
    path = OUT_DIR / "signal_lab_summary.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        notes = pd.DataFrame({"Item": [
            "Events analysed", "Tickers", "Date range", "Features x horizons tested",
            "Survive FDR (q<0.10)", "Same-sign out-of-sample"],
            "Value": [len(ev), ev["ticker"].nunique(),
                      f'{ev["call_date"].min()[:10]} to {ev["call_date"].max()[:10]}', len(res),
                      int(res["survives_fdr"].sum()), int(res["same_sign_oos"].sum())]})
        notes.to_excel(xw, sheet_name="Summary", index=False)
        res.round(4).to_excel(xw, sheet_name="Results", index=False)
        ev.head(500).to_excel(xw, sheet_name="Event sample", index=False)

        ws = xw.sheets["Results"]
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3864")
        ws.freeze_panes = "A2"
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 16
        ws.column_dimensions["A"].width = 30

        # chart: train vs test IC for the 10 strongest features (the honest picture)
        top = min(10, len(res)); ic_tr = res.columns.get_loc("ic_train") + 1
        ch = BarChart(); ch.title = "Information coefficient: train vs. test (top 10 by p-value)"
        ch.add_data(Reference(ws, min_col=ic_tr, max_col=ic_tr + 1, min_row=1, max_row=top + 1), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=top + 1))
        ch.width, ch.height = 24, 10
        ws.add_chart(ch, "A15" if top < 12 else "A30")
    print("Wrote", path)

if __name__ == "__main__":
    run()
