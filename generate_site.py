import csv, os, shutil, datetime
from jinja2 import Environment, FileSystemLoader

SITE_URL = "https://www.combien-coute.net"  # ← mets ton domaine

ROOT = os.path.dirname(__file__)
TPL = os.path.join(ROOT, "templates")

DATA_DIR = os.path.join(ROOT, "data")
CATEGORIES_CSV = os.path.join(DATA_DIR, "categories.csv")
VILLES_CSV = os.path.join(DATA_DIR, "villes.csv")
PRIX_CSV = os.path.join(DATA_DIR, "prix.csv")

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def build(out_dir):
    env = Environment(loader=FileSystemLoader(TPL))
    year = datetime.datetime.now().year

    categories = read_csv(CATEGORIES_CSV)
    villes = read_csv(VILLES_CSV)
    prix = read_csv(PRIX_CSV)

    # pays
    countries_map = {}
    for v in villes:
        countries_map[v["country_slug"]] = v["country_name"]
    countries = [{"slug": s, "name": n} for s, n in sorted(countries_map.items(), key=lambda x:x[1].lower())]

    # index
    html = env.get_template("index.html.j2").render(
        title="",
        description="",
        categories=categories,
        countries=countries,
        year=year
    )
    write_page(env, out_dir, "index.html", html)

    # dossiers
    ensure_dir(os.path.join(out_dir, "categories"))
    ensure_dir(os.path.join(out_dir, "countries"))
    ensure_dir(os.path.join(out_dir, "cities"))

    # helpers
    ville_by_slug = {v["city_slug"]: v for v in villes}
    cat_by_slug = {c["slug"]: c for c in categories}
    prices_by_city_cat = {}
    for p in prix:
        key = (p["city_slug"], p["category_slug"])
        prices_by_city_cat[key] = p

    # pages catégorie
    for c in categories:
        rows = []
        for v in villes:
            p = prices_by_city_cat.get((v["city_slug"], c["slug"]))
            rows.append({
                "city_name": v["city_name"],
                "value": float(p["value"]) if p else None
            })
        html = env.get_template("category.html.j2").render(
            title="",
            description="",
            category=c,
            rows=rows,
            year=year
        )
        write_page(env, os.path.join(out_dir, "categories"), f"{c['slug']}.html", html)

    # pages pays
    for co in countries:
        cities = [ {"slug": v["city_slug"], "name": v["city_name"]}
                   for v in villes if v["country_slug"] == co["slug"] ]
        html = env.get_template("country.html.j2").render(
            title="",
            description="",
            country=co,
            cities=cities,
            year=year
        )
        write_page(env, os.path.join(out_dir, "countries"), f"{co['slug']}.html", html)

    # pages villes
    for v in villes:
        rows = []
        for c in categories:
            p = prices_by_city_cat.get((v["city_slug"], c["slug"]))
            rows.append({
                "slug": c["slug"],
                "name": c["name"],
                "unit": c.get("unit") or "",
                "value": float(p["value"]) if p else None
            })
        html = env.get_template("city.html.j2").render(
            title="",
            description="",
            city={"slug": v["city_slug"], "name": v["city_name"]},
            rows=rows,
            year=year
        )
        write_page(env, os.path.join(out_dir, "cities"), f"{v['city_slug']}.html", html)

    # sitemap.xml
    sm = env.get_template("sitemap.xml.j2").render(
        site_url=SITE_URL,
        categories=categories,
        countries=countries,
        cities=[{"slug": v["city_slug"]} for v in villes]
    )
    with open(os.path.join(out_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm)

    # robots.txt
    robots = env.get_template("robots.txt.j2").render(site_url=SITE_URL)
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    # ads.txt : on copie celui à la racine du repo si présent
    src_ads = os.path.join(ROOT, "ads.txt")
    if os.path.exists(src_ads):
        shutil.copyfile(src_ads, os.path.join(out_dir, "ads.txt"))

def write_page(env, out_dir, filename, html):
    with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    # sortie : le repo GitHub Pages à côté (adapte si besoin)
    OUT = os.path.abspath(os.path.join(ROOT, "..", "yug2704.github.io"))
    ensure_dir(OUT)
    build(OUT)
    print("Site généré →", OUT)
