import os, datetime, pandas as pd
from jinja2 import Environment, FileSystemLoader

OUTPUT_DIR = "public"
BASE_URL = "https://yug2704.github.io/cost-of-living"  # <-- bien en prod

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

def main():
    villes = pd.read_csv("data/villes.csv")
    prix = pd.read_csv("data/prix.csv")
    df = villes.merge(prix, on="slug")
    page_tpl = env.get_template("page.html.j2")
    index_tpl = env.get_template("index.html.j2")

    os.makedirs(f"{OUTPUT_DIR}/villes", exist_ok=True)
    year = datetime.date.today().year
    date_maj = datetime.date.today().strftime("%Y-%m-%d")

    urls = []
    # --- Génère 1 page par ville ---
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
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        urls.append(f"{BASE_URL}/villes/{r['slug']}.html")

    # --- Génère la page d'accueil stylisée ---
    villes_list = df[["ville", "slug"]].to_dict("records")
    index_html = index_tpl.render(
        villes=villes_list,
        base_url=BASE_URL,
        annee=year,
    )
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"Généré {len(urls)} pages + index !")

if __name__ == "__main__":
    main()
