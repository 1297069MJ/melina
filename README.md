# Hispanic Heritage Historical Data Explorer

A Streamlit student research app that retrieves World Bank historical indicators, supports editable scenario data, fits centered-time polynomial models, calculates estimates, compares countries, explores derivatives, and exports CSV/XLSX/PDF reports.

## Files
- `app.py` — complete Streamlit app.
- `requirements.txt` — minimal unpinned dependencies.
- `sources.md` — data definitions and source links.

## Run locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, and `sources.md` to its root.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy. Check the app logs if dependency installation or startup fails.
5. Every pushed commit to the selected branch can trigger a redeploy.

## Deploy to Render
1. Create a GitHub repository containing the same files.
2. In Render, choose **New + → Web Service**, connect the repository, and select Python.
3. Build command:

   `pip install -r requirements.txt`

4. Start command (paste as one line):

   `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT`

5. Deploy and open the generated `onrender.com` URL. Streamlit Community Cloud is the simplest Streamlit-native deployment; Render works as a Python web service. A free instance may sleep or have cold starts depending on Render's current plan.

## Research question and choices
Before presenting, replace the team's planning notes with a clear research question, selected countries, indicator, and mathematics pathway. Example: “How has life expectancy changed in Mexico compared with Brazil and Chile over the available historical period, and how well does a polynomial summarize that trend?” Choose the question based on what the data actually contain.

## Data and modeling notes
- The requested window is current year minus 70 through current year minus 1. The app reports actual non-null coverage rather than claiming every year exists.
- World Bank values may be missing. Missing observations are not replaced with invented data.
- The editable table is separate from the fetched source. If edited, the app marks the analysis as a user-modified scenario. Use **Reset edited data to source** to restore the fetched table.
- Polynomial time is centered at the first valid year, `t = year - base_year`, to improve numerical conditioning.
- R² and MAE are in-sample fit metrics. A chronological holdout MAE is shown only when enough observations are available.
- Extrapolations are model outputs, not forecasts guaranteed to occur. High-degree polynomials can oscillate and can produce implausible values.
- The function lab uses SymPy to differentiate a selected expression. Root-finding and sign tests are partly numerical; results are labeled as candidates/approximations, and no automated numerical routine can guarantee detection of every discontinuity or extremum.
- The contextual visuals are schematic teaching aids, not validated physical, medical, financial, or weather simulations.
- No credentials are needed. Do not put API keys or secrets in the source code.

## Verification checklist
- [ ] Confirm indicator label, units, definition, country, and API URL match `sources.md`.
- [ ] Confirm retrieved years are within the requested window and the displayed count matches non-null rows.
- [ ] Edit a value, confirm the user-modified warning appears, then reset to source.
- [ ] Try a duplicate year, non-integer year, missing value, and nonnumeric value; confirm validation blocks fitting.
- [ ] Select a degree with too few distinct observations; confirm fitting is blocked with an explanation.
- [ ] Check that the equation uses `t = year - base_year`; compare fitted values against the chart and residual table.
- [ ] Calculate a single year, then include that year in batch results; the estimates should agree.
- [ ] Test malformed custom function text and a rational function with a discontinuity.
- [ ] Change each selector/slider and confirm the corresponding chart, equation, output, or report changes.
- [ ] Download and open CSV, XLSX, and PDF; verify the XLSX has Summary, Working data, Calculated years, and Residuals sheets.
- [ ] Deploy and check logs, page load, data retrieval, and downloads on the hosted app.

## Common problems
- **API/network error:** check World Bank API status/connectivity and retry; the app does not fill missing values with fake data.
- **Insufficient observations:** lower the polynomial degree or choose an indicator/country with enough distinct years.
- **Excel/PDF download fails:** check dependency install logs for `xlsxwriter` or `reportlab`.
- **SymPy parsing error:** use `x`, `+ - * / **`, parentheses, and supported functions such as `sin`, `cos`, `exp`, `log`, and `sqrt`.
- **Render port error:** ensure the start command uses `$PORT` and `--server.address=0.0.0.0`.
- **Slow startup:** check Render/Streamlit logs and allow for the first dependency installation and first API request.

## How the app works
1. Streamlit controls choose a country, indicator, degree, marker increment, and extrapolation horizon.
2. A cached `requests` call fetches the World Bank API data.
3. The source table is copied into a separately editable working table.
4. Validation checks years, duplicates, numeric values, and selected indicator constraints.
5. NumPy fits a polynomial to centered years; pandas stores residuals and calculated results.
6. Matplotlib produces charts; SymPy handles symbolic derivatives in the function lab.
7. ReportLab creates a PDF, XlsxWriter creates an Excel workbook, and pandas creates CSV files.

## Limitations to explain to the class
This is a research and mathematics demonstration, not a causal inference tool. Historical correlations do not prove causes. National indicators can have methodological breaks, revised estimates, missing years, and different coverage. Polynomial fits can be poor near turning points and are especially unreliable outside the observed range. Derivative and extremum checks in the general function lab are numerical aids, not a formal proof system. Review the source metadata and limitations before interpreting results.


## Website appearance customization
The sidebar includes **Website appearance** controls for choosing a font (Inter, Poppins, Lora, Merriweather, Roboto Mono, or system default) and a background palette (Clean light, Midnight blue, Warm paper, Ocean mist, Lavender, or Forest). These options change presentation only; they do not change the underlying data, model, or exports. Google Fonts are loaded from Google Fonts when the deployed browser has network access; fallback fonts are specified for offline or blocked requests.
