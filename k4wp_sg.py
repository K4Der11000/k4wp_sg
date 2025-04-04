import requests import cloudscraper import re import json import threading import tkinter as tk from tkinter import scrolledtext, filedialog, messagebox from bs4 import BeautifulSoup

تحديث قائمة البروكسيات

PROXY_SOURCES = [ "https://www.proxy-list.download/api/v1/get?type=http", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt" ] PROXIES_LIST = []

def update_proxies(): global PROXIES_LIST new_proxies = []

for url in PROXY_SOURCES:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxy_list = response.text.strip().split("\n")
            new_proxies.extend(proxy_list)
    except:
        pass

PROXIES_LIST = new_proxies

def get_random_proxy(): if not PROXIES_LIST: update_proxies() if PROXIES_LIST: proxy = random.choice(PROXIES_LIST) return {"http": f"http://{proxy}", "https": f"http://{proxy}"} return {}

def check_wordpress(url): if not url.startswith("http"): url = "http://" + url

result = f"<h2>فحص الموقع: {url}</h2>\n"
try:
    scraper = cloudscraper.create_scraper()
    proxy = get_random_proxy()
    response = scraper.get(url, proxies=proxy, timeout=10)
    
    if response.status_code != 200:
        result += "<p style='color:red;'>[!] تعذر الوصول إلى الموقع.</p>\n"
        return result

    if "wp-content" in response.text or "wp-includes" in response.text:
        result += "<p style='color:green;'>[+] الموقع يستخدم WordPress.</p>\n"
    else:
        result += "<p style='color:red;'>[-] الموقع لا يبدو أنه WordPress.</p>\n"
        return result

    soup = BeautifulSoup(response.text, "html.parser")
    generator = soup.find("meta", {"name": "generator"})
    if generator and "WordPress" in generator.get("content", ""):
        wp_version = generator["content"].split("WordPress ")[-1]
        result += f"<p>[+] إصدار WordPress: <b>{wp_version}</b></p>\n"
    
    plugins = set(re.findall(r'/wp-content/plugins/([a-zA-Z0-9-_]+)/', response.text))
    result += "<h3>الإضافات المكتشفة:</h3><ul>" + "".join(f"<li>{p}</li>" for p in plugins) + "</ul>\n"
    
    themes = set(re.findall(r'/wp-content/themes/([a-zA-Z0-9-_]+)/', response.text))
    result += "<h3>القوالب المكتشفة:</h3><ul>" + "".join(f"<li>{t}</li>" for t in themes) + "</ul>\n"

except requests.RequestException:
    result += "<p style='color:red;'>[!] خطأ أثناء الفحص.</p>\n"
return result

def scan_sites(): urls = entry_sites.get("1.0", tk.END).strip().split("\n") output_text.delete("1.0", tk.END) global results_html results_html = "<html><head><meta charset='utf-8'><title>نتائج الفحص</title></head><body>"

for url in urls:
    if url.strip():
        result = check_wordpress(url.strip())
        output_text.insert(tk.END, result + "\n" + "-"*50 + "\n")
        results_html += result + "<hr>"

results_html += "</body></html>"

def save_results(): file_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")]) if file_path: with open(file_path, "w", encoding="utf-8") as file: file.write(results_html)

إنشاء الواجهة الرسومية

root = tk.Tk() root.title("فاحص WordPress") root.geometry("600x500")

tk.Label(root, text="أدخل عناوين المواقع (كل موقع في سطر):").pack() entry_sites = scrolledtext.ScrolledText(root, height=5) entry_sites.pack(fill=tk.BOTH, padx=5, pady=5)

tk.Button(root, text="تحميل قائمة من ملف", command=load_sites_from_file).pack() tk.Button(root, text="بدء الفحص", command=lambda: threading.Thread(target=scan_sites).start()).pack()

tk.Label(root, text="النتائج:").pack() output_text = scrolledtext.ScrolledText(root, height=15) output_text.pack(fill=tk.BOTH, padx=5, pady=5)

tk.Button(root, text="حفظ النتائج", command=save_results).pack()

tk.Button(root, text="خروج", command=root.quit).pack()

root.mainloop()

