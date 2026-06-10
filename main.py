import logging
import time
import sqlite3
import random
import re
import threading
import csv
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk, messagebox
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

class ProductDTO:
    def __init__(self, item_id: str, title: str, price: float, url: str):
        self.item_id = item_id
        self.title = title
        self.price = price
        self.url = url


class SQLiteRepository:
    def __init__(self, db_path="base.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    url TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_or_update_product(self, product: ProductDTO) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_price FROM products WHERE id = ?", (product.item_id,))
            row = cursor.fetchone()

            if not row:
                cursor.execute(
                    "INSERT INTO products (id, title, current_price, url) VALUES (?, ?, ?, ?)",
                    (product.item_id, product.title, product.price, product.url)
                )
                conn.commit()
                return "new"
            else:
                old_price = float(row[0])
                if old_price != product.price:
                    cursor.execute(
                        "UPDATE products SET current_price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                        (product.price, product.item_id)
                    )
                    conn.commit()
                    return "updated"
        return "none"

    def get_all_products(self, order_by="updated_at DESC"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, title, current_price, url FROM products ORDER BY {order_by}")
            return cursor.fetchall()


class VintedParserEngine:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

    def extract_catalog(self, url: str, status_callback=None) -> list[ProductDTO]:
        extracted_products = []
        
        with sync_playwright() as p:
            if status_callback: status_callback("Launching headless Chromium browser...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={"width": 1280, "height": 900}
            )
            
            page = context.new_page()
            if status_callback: status_callback("Connecting to Vinted...")
            
            try:
                page.goto(url, wait_until="load", timeout=30000)
                time.sleep(3)
                
                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4);")
                time.sleep(2)
                
                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                
                items = soup.find_all("div", {"data-testid": "grid-item"}) or soup.find_all("div", class_="feed-grid__item")
                if status_callback: status_callback(f"Found {len(items)} elements. Parsing structure...")
                
                for item in items:
                    try:
                        link_tag = item.find("a", href=re.compile(r"/items/")) or item.find("a")
                        if not link_tag or 'href' not in link_tag.attrs: continue
                            
                        product_url = link_tag["href"]
                        if not product_url.startswith("http"):
                            product_url = "https://www.vinted.com" + product_url
                        
                        id_match = re.search(r"/items/(\d+)", product_url)
                        item_id = id_match.group(1) if id_match else product_url.split("/")[-1].split("-")[0]

                        price = 0.0
                        all_texts = [t.text.strip() for t in item.find_all(string=True) if t.text.strip()]
                        for text in all_texts:
                            if any(c in text for c in ["$", "€", "£", "zł"]) or re.search(r"\d+[\.,]\d+", text):
                                price_digits = "".join(re.findall(r"[\d.,]+", text)).replace(",", ".")
                                if price_digits.count(".") > 1:
                                    parts = price_digits.split(".")
                                    price_digits = "".join(parts[:-1]) + "." + parts[-1]
                                try:
                                    price = float(price_digits)
                                    if price > 0: break
                                except ValueError: continue

                        title = link_tag.get("title", "").strip() or (all_texts[1] if len(all_texts) > 1 else "Item")

                        if price > 0:
                            dto = ProductDTO(item_id=item_id, title=title, price=price, url=product_url)
                            extracted_products.append(dto)
                    except Exception:
                        continue
                        
            except Exception as e:
                logging.error(f"Browser engine error: {e}")
            finally:
                context.close()
                browser.close()
                
        return extracted_products


class VintedAppGUI:
    def __init__(self, root, engine: VintedParserEngine, repo: SQLiteRepository):
        self.root = root
        self.engine = engine
        self.repo = repo
        
        self.root.title("Vinted Data Pipeline Monitor Pro")
        self.root.geometry("900x600")
        self.root.configure(bg="#f4f6f9")
        
        self.current_sort = "updated_at DESC"
        self.is_auto_running = False
        
        self._create_widgets()
        self._load_data_from_db()

    def _create_widgets(self):
        top_frame = tk.Frame(self.root, bg="#f4f6f9", pady=10)
        top_frame.pack(fill="x", padx=15)
        
        tk.Label(top_frame, text="Vinted Catalog URL:", bg="#f4f6f9", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        self.url_entry = tk.Entry(top_frame, font=("Arial", 10), width=45)
        self.url_entry.insert(0, "https://www.vinted.com/catalog?category_id=1242")
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.start_btn = tk.Button(top_frame, text="Run Parser", bg="#007bff", fg="white", font=("Arial", 10, "bold"), command=self._start_pipeline_thread, relief="flat", padx=10)
        self.start_btn.pack(side="left", padx=5)

        self.export_btn = tk.Button(top_frame, text="Export to CSV", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=self._export_to_csv, relief="flat", padx=10)
        self.export_btn.pack(side="left", padx=5)

        auto_frame = tk.Frame(self.root, bg="#f4f6f9")
        auto_frame.pack(fill="x", padx=15, pady=2)
        
        self.auto_var = tk.BooleanVar()
        self.auto_check = tk.Checkbutton(auto_frame, text="Enable auto-scraping every", variable=self.auto_var, bg="#f4f6f9", font=("Arial", 9), command=self._toggle_auto_mode)
        self.auto_check.pack(side="left")
        
        self.interval_combo = ttk.Combobox(auto_frame, values=["5 min", "15 min", "30 min"], width=7, state="readonly")
        self.interval_combo.set("15 min")
        self.interval_combo.pack(side="left", padx=5)

        self.status_label = tk.Label(self.root, text="Status: Idle", bd=1, relief="sunken", anchor="w", bg="#e9ecef", font=("Arial", 9, "italic"))
        self.status_label.pack(side="bottom", fill="x")

        table_frame = tk.Frame(self.root, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        columns = ("id", "title", "price", "url")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="Item ID ↕", command=lambda: self._sort_column("id"))
        self.tree.heading("title", text="Title / Description ↕", command=lambda: self._sort_column("title"))
        self.tree.heading("price", text="Price ↕", command=lambda: self._sort_column("current_price"))
        self.tree.heading("url", text="URL")
        
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("title", width=350, anchor="w")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("url", width=250, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _update_status(self, text):
        self.status_label.config(text=f"Status: {text}")
        self.root.update_idletasks()

    def _load_data_from_db(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        products = self.repo.get_all_products(order_by=self.current_sort)
        for p in products:
            self.tree.insert("", "end", values=p)

    def _sort_column(self, col_name):
        if col_name in self.current_sort and "ASC" in self.current_sort:
            self.current_sort = f"{col_name} DESC"
        else:
            self.current_sort = f"{col_name} ASC"
        self._load_data_from_db()

    def _export_to_csv(self):
        products = self.repo.get_all_products()
        if not products:
            messagebox.showwarning("Export", "Database is empty! Nothing to export.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Report")
        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Item ID", "Title", "Price", "URL"])
                    writer.writerows(products)
                messagebox.showinfo("Export", "Data successfully exported to CSV file!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file: {e}")

    def _toggle_auto_mode(self):
        if self.auto_var.get():
            self.is_auto_running = True
            self._run_auto_cycle()
        else:
            self.is_auto_running = False
            self._update_status("Auto-scraping disabled.")

    def _run_auto_cycle(self):
        if not self.is_auto_running:
            return
            
        self._start_pipeline_thread()
        
        interval_text = self.interval_combo.get()
        minutes = int(interval_text.split()[0])
        ms_interval = minutes * 60 * 1000
        
        self.root.after(ms_interval, self._run_auto_cycle)

    def _start_pipeline_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Please enter a valid catalog URL.")
            return
            
        self.start_btn.config(state="disabled")
        thread = threading.Thread(target=self._run_pipeline, args=(url,), daemon=True)
        thread.start()

    def _run_pipeline(self, url):
        try:
            self._update_status("Initializing data pipeline...")
            products = self.engine.extract_catalog(url, status_callback=self._update_status)
            
            self._update_status(f"Processing database for {len(products)} records...")
            new_count = 0
            updated_count = 0
            
            for p in products:
                status = self.repo.save_or_update_product(p)
                if status == "new": new_count += 1
                elif status == "updated": updated_count += 1
            
            self._load_data_from_db()
            self._update_status(f"Done! Added new: {new_count}, Prices updated: {updated_count}")
            
            if not self.auto_var.get():
                messagebox.showinfo("Success", f"Pipeline finished!\nNew products: {new_count}\nPrices updated: {updated_count}")
            
        except Exception as e:
            self._update_status(f"Critical pipeline error: {e}")
            if not self.auto_var.get():
                messagebox.showerror("Error", f"Pipeline execution failed:\n{e}")
        finally:
            self.start_btn.config(state="normal")


if __name__ == "__main__":
    db_repo = SQLiteRepository(db_path="base.db")
    parser_engine = VintedParserEngine()
    
    root_window = tk.Tk()
    app = VintedAppGUI(root=root_window, engine=parser_engine, repo=db_repo)
    root_window.mainloop()