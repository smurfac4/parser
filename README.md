
---

# Vinted Data Pipeline Monitor Pro

A high-performance, robust desktop application built in Python designed to scrape, monitor, and cache product listing data from Vinted catalogs in real-time. The application features a native Graphical User Interface (GUI), structured logging, local persistent caching via SQLite, multi-threaded performance, an automated background scheduler, and interactive reporting tools.

---

## 🚀 Core Features

* **Intelligent Web Scraping:** Driven by **Playwright (Headless Chromium)** and **BeautifulSoup4** to bypass rendering roadblocks and safely extract active catalog layouts.
* **Adaptive Structural Analysis:** Features custom heuristic pricing algorithms that automatically identify, filter, and normalize multiple global currencies (`$`, `€`, `£`, `zł`, etc.) regardless of unexpected CSS layout updates.
* **Threaded Architecture:** Heavy background browser workloads run concurrently via specialized Python `threading` routines, maintaining a highly responsive UI context.
* **Persistent Storage (SQLite Engine):** Embeds a low-latency relational datastore (`base.db`) utilizing an **Upsert operational model** to separate raw product data insertion from incremental cost variations.
* **Automated Background Scheduler:** Allows continuous background operation at localized runtime loops (5, 15, or 30-minute intervals) without blocking interactive UI controls.
* **Advanced Data Tree UI:** Features native interactive sorting headers (`ID`, `Title`, `Price`) mapped seamlessly via dynamic SQL binding rules.
* **Industrial Reporting Tool:** Complete production-ready **CSV Exporter** supporting direct downloads of data cache targets straight to local storage arrays.

---

## 🛠️ Technology Stack

* **Core Logic:** Python 3.x
* **Browser Automation Engine:** Playwright (Headless Chromium)
* **HTML Parser Layer:** BeautifulSoup4 (with regular expression optimizations)
* **Database Management System:** SQLite3
* **User Interface Layer:** Tkinter / TTK (Native Desktop System Styles)
* **Asynchronous Contexts:** Native Threading Modules

---

## 📦 System Installation & Environment Setup

Follow these streamlined instructions to clone, establish environments, and safely install required application dependencies on local systems.

### 1. Install Project Dependencies

Open your shell environment (or PowerShell in VS Code) and ensure your Python package manager installs the mandatory packages:

```bash
pip install playwright beautifulsoup4

```

### 2. Configure Local Chromium Binaries

Initialize Playwright's system profile to safely register the matching automated core dependencies:

```bash
playwright install chromium

```

---

## 🖥️ Execution Guidelines

To run the application, navigate to the target module directory (`/parser`) containing your configured executable block and run:

```bash
python main.py

```

### 💡 Troubleshooting PowerShell Call Constraints

If your underlying Windows Terminal restriction flags path execution parsing errors (`AmpersandNotAllowed`), bypass the path variable parser via native application process routines directly:

```powershell
Start-Process "python" -ArgumentList "main.py" -NoNewWindow -Wait

```

---

## 📊 Application Interface Workflows

1. **Target Analysis Setup:** Paste your intended Vinted category link into the designated **Vinted Catalog URL** text entry field.
2. **Execute Scrape Cycles:** Click **Run Parser** to trigger the headless automation engine thread. Live operation status notifications will populate on the integrated Status Bar.
3. **Analyze & Sort Metrics:** Click individual table header tabs (`Item ID ↕`, `Title / Description ↕`, `Price ↕`) to dynamically sort all parsed product records.
4. **Deploy Background Tasks:** Check the **Enable auto-scraping** tickbox, specify your timing threshold, and let the background worker manage continuous tracking cycles silently.
5. **Generate File Reports:** Click **Export to CSV** to compile, save, and download your stored localized dataset files into standard standalone office documents 