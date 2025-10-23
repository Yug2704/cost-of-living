import os
import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# --- Réglages ---
OUTPUT_DIR = "public"
BASE_URL = "https://yug2704.github.io/cost-of-living"  # domaine en ligne

# Jinja cherche les templates dans /templates
env = Environment(loader=FileSystemLoader("templates"))

# ---------- Utilitaires ----------
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def budget_estime(row: pd.Series) -> float:
    """
    loyer centre + utilities + internet + transport + 10 x repas
    (protégé contre les NaN)
    """
    def val(x): 
        return 0 if pd.isna(x) else float(x)
    total = (
        val(row.get("rent_1br_center"))
        + val(row.get("utilities_apt"))
        + val(row.get("internet"))
        + val(row.get("transport_monthly"))
        + 10 * val(row.get("meal_inexpensive"))
    )
    return round(total, 0)

def make_sitemap(urls: list[str]) -> str:
    items = "\n".join(
        f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>"
        for u in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE_URL}/</loc><changefreq>weekly</changefreq></url>
{items}
</urlset>"""

# ---------- Programme principal ----------
def main():
    # Données
    villes = pd.read_csv("data/villes.csv")
    prix = pd.read_csv("data/prix.csv")
    df = villes.merge(prix, on="slug", how="inner")

    # Templates
    page_tpl = env.get_template("page.html.j2")
    index_tpl = env.get_template("index.html.j2")

    # Sorties
    ensure_dir(f"{OUTPUT_DIR}/villes")

    # Contexte commun
    today = datetime.date.today()
    year = today.year
    date_maj = today.strftime("%Y-%m-%d")

    urls: list[str] = []

    # --- Génération des pages ville ---
    for _, r in df.iterrows():
        html = page_tpl.render(
            # Données ville
            ville=r["ville"],
            devise=r.get("devise", "EUR"),
            rent_1br_center=r.get("rent_1br_center", "-"),
            rent_1br_outside=r.get("rent_1br_outside", "-"),
            utilities_apt=r.get("utilities_apt", "-"),
            internet=r.get("internet", "-"),
            transport_monthly=r.get("transport_monthly", "-"),
            meal_inexpensive=r.get("meal_inexpensive", "-"),
            cappuccino=r.get("cappuccino", "-"),
            bread=r.get("bread", "-"),
            eggs12=r.get("eggs12", "-"),
            gasoline=r.get("gasoline", "-"),

            # Contexte
            budget_estime=budget_estime(r),
            date_maj=date_maj,
            annee=year,

            # >>> Variables SEO attendues par le template
            base_url=BASE_URL,
            canonical=f"{BASE_URL}/villes/{r['slug']}.html",
        )
        out_path = f"{OUTPUT_DIR}/villes/{r['slug']}.html"
        write_file(out_path, html)
        urls.append(f"{BASE_URL}/villes/{r['slug']}.html")

    # --- Page d’accueil (index) ---
    villes_list = df[["ville", "slug"]].sort_values("ville").to_dict("records")
    index_html = index_tpl.render(villes=villes_list, base_url=BASE_URL, annee=year)
    write_file(f"{OUTPUT_DIR}/index.html", index_html)

    # --- Sitemap & robots ---
    sitemap_xml = make_sitemap(urls)
    write_file(f"{OUTPUT_DIR}/sitemap.xml", sitemap_xml)

    robots_txt = f"Sitemap: {BASE_URL}/sitemap.xml\nUser-agent: *\nAllow: /\n"
    write_file(f"{OUTPUT_DIR}/robots.txt", robots_txt)

    print(f"Généré {len(urls)} pages ville + index + sitemap + robots.txt")

if __name__ == "__main__":
    main()
