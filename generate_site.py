import os, datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader

OUTPUT_DIR = "public"
BASE_URL = "https://yug2704.github.io/cost-of-living"  # à jour chez toi

env = Environment(loader=FileSystemLoader("templates"))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def budget_estime(row: pd.Series) -> float:
    def v(x): return 0 if pd.isna(x) else float(x)
    total = v(row.get("rent_1br_center")) + v(row.get("utilities_apt")) + v(row.get("internet")) + v(row.get("transport_monthly")) + 10*v(row.get("meal_inexpensive"))
    return round(total, 0)

def load_df():
    villes = pd.read_csv("data/villes.csv")
    prix = pd.read_csv("data/prix.csv")
    return villes.merge(prix, on="slug", how="inner")

def make_sitemap(urls):
    items = "\n".join([f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>" for u in urls])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE_URL}/</loc><changefreq>weekly</changefreq></url>
{items}
</urlset>"""

def main():
    df = load_df().copy()
    today = datetime.date.today()
    year = today.year
    date_maj = today.strftime("%Y-%m-%d")

    # TEMPLATES
    tpl_fr = env.get_template("page.html.j2")
    tpl_en = env.get_template("page_en.html.j2")
    idx_fr = env.get_template("index.html.j2")       # tu l'as déjà
    idx_en = env.get_template("index_en.html.j2")    # nouveau

    # Sorties
    ensure_dir(f"{OUTPUT_DIR}/villes")
    ensure_dir(f"{OUTPUT_DIR}/en/cities")

    urls = []

    # ----- FR pages -----
    for _, r in df.iterrows():
        fr_url = f"{BASE_URL}/villes/{r['slug']}.html"
        en_url = f"{BASE_URL}/en/cities/{r['slug']}.html"

        html_fr = tpl_fr.render(
            ville=r["ville"], devise=r.get("devise","EUR"),
            rent_1br_center=r.get("rent_1br_center","-"),
            rent_1br_outside=r.get("rent_1br_outside","-"),
            utilities_apt=r.get("utilities_apt","-"),
            internet=r.get("internet","-"),
            transport_monthly=r.get("transport_monthly","-"),
            meal_inexpensive=r.get("meal_inexpensive","-"),
            cappuccino=r.get("cappuccino","-"),
            bread=r.get("bread","-"),
            eggs12=r.get("eggs12","-"),
            gasoline=r.get("gasoline","-"),
            budget_estime=budget_estime(r),
            date_maj=date_maj, annee=year,
            base_url=BASE_URL,
            canonical=fr_url,              # ton template FR attend "canonical"
            canonical_url=fr_url,          # et parfois "canonical_url" -> on met les deux
        )
        out_fr = f"{OUTPUT_DIR}/villes/{r['slug']}.html"
        write_file(out_fr, html_fr)
        urls.append(fr_url)

        # ----- EN pages -----
        html_en = tpl_en.render(
            ville=r["ville"], devise=r.get("devise","EUR"),
            rent_1br_center=r.get("rent_1br_center","-"),
            rent_1br_outside=r.get("rent_1br_outside","-"),
            utilities_apt=r.get("utilities_apt","-"),
            internet=r.get("internet","-"),
            transport_monthly=r.get("transport_monthly","-"),
            meal_inexpensive=r.get("meal_inexpensive","-"),
            cappuccino=r.get("cappuccino","-"),
            bread=r.get("bread","-"),
            eggs12=r.get("eggs12","-"),
            gasoline=r.get("gasoline","-"),
            budget_estime=budget_estime(r),
            date_maj=date_maj, annee=year,
            base_url=BASE_URL,
            canonical_en=en_url,
            canonical_fr=fr_url,
        )
        out_en = f"{OUTPUT_DIR}/en/cities/{r['slug']}.html"
        write_file(out_en, html_en)
        urls.append(en_url)

    # ----- Index FR -----
    villes_list = df[["ville","slug"]].sort_values("ville").to_dict("records")
    html_idx_fr = idx_fr.render(villes=villes_list, base_url=BASE_URL, annee=year, date_maj=date_maj)
    write_file(f"{OUTPUT_DIR}/index.html", html_idx_fr)

    # ----- Index EN -----
    html_idx_en = idx_en.render(villes=villes_list, base_url=BASE_URL, annee=year, date_maj=date_maj)
    write_file(f"{OUTPUT_DIR}/en/index.html", html_idx_en)

    # ----- sitemap & robots -----
    sitemap = make_sitemap(urls)
    write_file(f"{OUTPUT_DIR}/sitemap.xml", sitemap)

    robots = f"Sitemap: {BASE_URL}/sitemap.xml\nUser-agent: *\nAllow: /\n"
    write_file(f"{OUTPUT_DIR}/robots.txt", robots)

    print(f"Generated FR+EN: {len(urls)} URLs, index & sitemap OK")

if __name__ == "__main__":
    main()
