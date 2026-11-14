# DATA INSIGHT — Interactive Data Analysis & Visualization System

A standalone, offline-capable Python desktop application for importing tabular datasets, reviewing data quality, cleaning a working copy, exploring descriptive statistics, generating charts and exporting results.

## 1. Objectives

- Make exploratory data analysis accessible without writing Python analysis code.
- Support CSV and Excel datasets.
- Keep the uploaded source data intact while cleaning a separate working copy.
- Present descriptive statistics and visualizations in a desktop interface.
- Export reusable datasets, summaries and chart images.

## 2. Features

- Tkinter desktop interface with sidebar navigation.
- CSV, XLSX and XLS import; CSV encoding fallback; worksheet selection for multi-sheet workbooks.
- Overview cards, column types, missing-value counts, unique counts, duplicates and first 100 records.
- Cleaning: remove duplicates, drop incomplete rows, fill numeric mean/median, fill mode, rename/drop columns, convert types and reset to original.
- Descriptive statistics, quartiles, percentiles, correlation matrix and unique-value counts.
- Ten chart types: bar, horizontal bar, line, pie, scatter, histogram, box, area, heatmap and count plot.
- Chart color and title controls, embedded Matplotlib canvas and navigation toolbar.
- Automatically calculated descriptive insights.
- CSV, Excel, summary CSV, combined workbook, PNG and PDF export.
- Built-in synthetic sales dataset (350 records) with intentional missing values.

## 3. Technology stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Application language |
| Tkinter / ttk | Native desktop GUI |
| Pandas | Data import and analysis |
| NumPy | Numerical operations and sample data |
| Matplotlib | Charts and chart export |
| Seaborn | Statistical plotting |
| OpenPyXL | XLSX import/export |
| xlrd | Legacy XLS import |

All listed packages are free/open-source. Tkinter is included with many Python distributions; on some Linux distributions it must be installed separately (for example, `sudo apt install python3-tk`).

## 4. System requirements

- Windows 10/11, macOS, or Linux.
- Python 3.10 or newer recommended.
- Approximately 300 MB free disk space for Python and dependencies.
- Memory sufficient for the dataset being opened. Very large datasets may be slow because the app loads data into memory.
- Internet access is needed only to install packages or clone the repository; the application itself processes data locally and does not need internet access.

## 5. Folder structure

```text
Data_Visualization_System/
├── app.py
├── README.md
├── requirements.txt
├── sample_sales_dataset.csv
└── exports/
```

The `exports/` directory is the suggested default location for saved results. You can also choose another location in each save dialog.

## 6. Installation

Open a terminal in the project directory.

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate it

Windows Command Prompt:

```bat
.venv\Scripts\activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux Tkinter note

If Python reports that `tkinter` is unavailable, install your distribution's Tk package, for example:

```bash
sudo apt update
sudo apt install python3-tk
```

## 7. Run and close

Run from the project directory:

```bash
python app.py
```

Use **Exit Application** in the sidebar and confirm, or close the window using the window close control. Unsaved working-copy changes are discarded when the app closes; export any cleaned data you want to keep.

Deactivate the virtual environment when finished:

```bash
deactivate
```

## 8. Upload datasets

1. Select **Upload Dataset** in the sidebar.
2. Choose a `.csv`, `.xlsx` or `.xls` file.
3. For a workbook with multiple worksheets, enter the worksheet name from the displayed list.
4. A successful upload becomes the active dataset. Uploading another file replaces the active session dataset.
5. CSV files are tried with UTF-8 with BOM, UTF-8, Windows-1252 and Latin-1 encodings.

The application rejects empty datasets and unsupported file extensions. The original imported DataFrame is retained in memory as a reset point.

## 9. Data overview

Open **Data Overview** to see row and column counts, missing cells, duplicate rows, column data types, missing-value counts, unique counts and a preview of up to the first 100 rows. Horizontal and vertical scrollbars are available in the preview tables.

## 10. Clean datasets

Open **Data Cleaning**. Operations modify the working copy, not the original upload.

- **Missing-value report:** shows missing count and percentage for each column.
- **Remove duplicate rows:** removes exact duplicate records.
- **Drop rows with missing values:** removes rows with one or more missing cells.
- **Fill missing values:** choose a column and mean, median or mode. Mean and median are restricted to numeric columns; mode uses the first available mode.
- **Rename column:** choose a current column name and enter a unique replacement.
- **Remove column:** select a column to remove.
- **Convert type:** convert a column to numeric, datetime or string. Values that cannot be converted may become missing.
- **Reset to original:** discards working-copy edits and restores the original imported data.

Destructive operations request confirmation. Export the working dataset if you want to preserve the cleaned result.

## 11. Analyze datasets

Open **Data Analysis**.

The numerical summary includes count, mean, standard deviation, minimum, 10th percentile, first quartile, median, third quartile, 90th percentile and maximum. Range can be calculated as maximum minus minimum; variance is the square of standard deviation. Mode and categorical frequencies can be inspected in the Insights page and unique-value counts are shown alongside the correlation matrix.

The correlation matrix uses numeric columns only. Correlation measures association and is not proof of causation. Columns with insufficient valid observations can produce missing correlation values.

Use **Export statistical summary CSV** to save the numerical summary.

## 12. Create visualizations

Open **Visualization Studio** and select a chart, columns and aggregation where applicable. Set a title and optionally choose a chart color, then select **Generate chart**. The chart appears inside the application. Matplotlib's navigation toolbar provides pan, zoom, home, back/forward and save controls.

| Chart | Column guidance |
|---|---|
| Bar chart | Category X and numeric Y; choose aggregation |
| Horizontal bar chart | Category X and numeric Y; choose aggregation |
| Line chart | Category X and numeric Y; choose aggregation |
| Pie chart | Category X; displays up to 12 most frequent categories |
| Scatter plot | Numeric X and numeric Y |
| Histogram | Numeric X |
| Box plot | Numeric Y; optional category X |
| Area chart | Category X and numeric Y; choose aggregation |
| Heatmap | At least two numeric columns; displays their correlation matrix |
| Count plot | Select a categorical column in the Count plot category control |

Aggregation methods are sum, mean, count, median, minimum and maximum. Numeric requirements are checked before rendering. For charts with many categories, the display is limited to keep labels readable.

Select **Save chart** to export the current chart as a high-resolution PNG or PDF.

## 13. Interpret statistical results

- **Count:** number of non-missing observations.
- **Mean:** arithmetic average; can be affected by outliers.
- **Median:** middle value; often more robust to outliers.
- **Mode:** most frequent value.
- **Minimum / maximum:** smallest and largest observed values.
- **Quartiles / percentiles:** values below which a specified percentage of observations fall.
- **Standard deviation:** spread around the mean, in the same units as the data.
- **Variance:** squared standard deviation.
- **Correlation:** strength and direction of a linear association between numeric variables, from -1 to +1. It does not establish causality.

The Insights page reports observed values and frequent categories. Product/region-specific business insights are not assumed unless the dataset has a structure that supports them; review the underlying columns before drawing conclusions.

## 14. Export results

Open **Export Results**.

- Working dataset as CSV.
- Working dataset as Excel.
- Statistical summary as CSV.
- Complete Excel workbook with `Data`, `Statistics` and `Missing Values` sheets.

In Visualization Studio, save the active chart as PNG or PDF. Save dialogs allow you to choose the output path. The app does not overwrite the original uploaded source file automatically; choose a separate output filename.

## 15. Sample dataset

`sample_sales_dataset.csv` contains 350 deterministic synthetic order records with these fields:

`Order_ID`, `Date`, `Product`, `Category`, `Region`, `Quantity`, `Discount`, `Sales`, `Profit`, `Customer_Age`.

It includes a small number of intentionally missing values for practicing data-quality and cleaning operations. It is synthetic and does not represent real customers or business transactions. Select **Try sample dataset** on the Home page to load a newly generated sample in memory.

## 16. Troubleshooting

| Problem | Suggested action |
|---|---|
| `No module named pandas` (or another package) | Activate the environment and run `python -m pip install -r requirements.txt`. |
| `No module named tkinter` | Install the operating-system Tk package; on Debian/Ubuntu use `sudo apt install python3-tk`. |
| `.xls` import fails | Confirm `xlrd` is installed; run `python -m pip install xlrd`. |
| Excel file cannot be opened | Check that the workbook is valid and not password-protected or corrupted. |
| CSV characters look incorrect | Re-save as UTF-8 CSV, or try a compatible encoding in a spreadsheet editor. |
| Chart cannot be generated | Check the selected column types and ensure required numeric/category columns contain usable values. |
| Export permission error | Choose a folder where your account has write permission and ensure the destination file is not locked by another program. |
| App appears slow | Try a smaller dataset or remove unused columns before plotting. The application works in memory. |
| Linux display/Tk errors | Confirm Tkinter and a graphical desktop session are installed and available. |

## 17. Git: install, clone, update and remove

Install Git from <https://git-scm.com/downloads> (or your operating system's package manager), then verify:

```bash
git --version
```

Clone a repository (replace the example URL with the actual repository URL):

```bash
git clone https://github.com/Shankar-127/DATA_INSIGHT.git
cd REPOSITORY
```

Install and run as described above. To update an existing clone:

```bash
git pull
```

If dependencies changed, reinstall them:

```bash
python -m pip install -r requirements.txt
```

To remove the local clone, first close the application and move outside the repository folder, then delete the folder.

Windows Command Prompt:

```bat
rmdir /s /q REPOSITORY
```

Linux/macOS:

```bash
rm -rf REPOSITORY
```

These delete commands permanently remove the named local folder; double-check the path before running them. Git is not required to run DATA INSIGHT.

## 18. Limitations

- Datasets are loaded into memory; very large files can be slow or exceed available memory.
- No database server, cloud synchronization or multi-user collaboration is included.
- No predictive modelling or causal inference is performed.
- The application provides descriptive statistics and selected chart types, not a full statistical package.
- Legacy XLS support depends on `xlrd`.
- Excel macros are not executed; formulas are read as workbook values.
- The UI is designed to resize, but some controls may need additional space on small displays.

## 19. License information

The project files are supplied for educational use. No third-party package is bundled into the project. Python and each dependency are distributed under their own licenses; check their official license notices before redistributing a packaged copy. You may add a project license file if your institution or repository requires a specific license.
