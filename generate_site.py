import os, datetime, pandas as pd
from jinja2 import Environment, FileSystemLoader

OUTPUT_DIR = "public"
BASE_URL = "https://yug2704.github.io/cost-of-living"  # domaine en ligne

env = Environment(loader=FileSystemLoader("templates"))

def budget_estime(row):
    return round(
        (row["rent_1br_center"] or 0)
        + (row["utilities_apt"] or 0)
        + (row["internet"] or 0)
        + (row["transport_monthly"] or 0)
        + 10 * (row["meal_inexpensive"] or 0),
        0
    )

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def make_sitemap(urls):
    items = "\n".join([f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>" for u in urls])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE_URL}/</loc><changefreq>weekly</changefreq></url>
{items}
</urlset>"""

def main():
    # --- Données
    villes = pd.read_csv("data/villes.csv")
    prix = pd.read_csv("data/prix.csv")
    df = villes.merge(prix, on="slug")
    page_tpl = env.get_template("page.html.j2")
    index_tpl = env.get_template("index.html.j2")

    # --- Dossiers
    ensure_dir(f"{OUTPUT_DIR}/villes")

    # --- Contexte commun
    year = datetime.date.today().year
    date_maj = datetime.date.today().strftime("%Y-%m-%d")

    urls = []

    # --- Génère 1 page par ville
    for _, r in df.iterrows():
        html = page_tpl.render(
            ville=r["ville"],
            devise=r["devise"],
            rent_1br_center=r["rent_1br_center"],
            rent_1br_outside=r["rent_1br_outside"],
            utilities_apt=r["utilities_apt"],
            internet=r["internet"],
            transport_monthly=r["transport_monthly"],
            meal_inexpensive=r["meal_inexpensive"],
            cappuccino=r["cappuccino"],
            bread=r["bread"],
            eggs12=r["eggs12"],
            gasoline=r["gasoline"],
            budget_estime=budget_estime(r),
            date_maj=date_maj,
            annee=year,
        )
        out_path = f"{OUTPUT_DIR}/villes/{r['slug']}.html"
        write_file(out_path, html)
        urls.append(f"{BASE_URL}/villes/{r['slug']}.html")

    # --- Génère la page d'accueil
    villes_list = df[["ville", "slug"]].to_dict("records")
    index_html = index_tpl.render(
        villes=villes_list,
        base_url=BASE_URL,
        annee=year,
    )
    write_file(f"{OUTPUT_DIR}/index.html", index_html)

    # --- Génère sitemap.xml
    sitemap_xml = make_sitemap(urls)
    write_file(f"{OUTPUT_DIR}/sitemap.xml", sitemap_xml)

    # --- Génère robots.txt (pointe vers le sitemap)
    robots_txt = f"Sitemap: {BASE_URL}/sitemap.xml\nUser-agent: *\nAllow: /\n"
    write_file(f"{OUTPUT_DIR}/robots.txt", robots_txt)

    print(f"Généré {len(urls)} pages + index + sitemap + robots.txt")

if __name__ == "__main__":
    main()
