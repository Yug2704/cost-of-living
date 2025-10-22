import os, datetime, pandas as pd
from jinja2 import Environment, FileSystemLoader

OUTPUT_DIR = "public"
BASE_URL = "https://yug2704.github.io/cost-of-living"

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
    tpl = env.get_template("page.html.j2")

    os.makedirs(f"{OUTPUT_DIR}/villes", exist_ok=True)
    urls = []

    for _, r in df.iterrows():
        html = tpl.render(
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
            date_maj=datetime.date.today().strftime("%Y-%m-%d"),
            annee=datetime.date.today().year,
        )
        path = f"{OUTPUT_DIR}/villes/{r['slug']}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        urls.append(f"{BASE_URL}/villes/{r['slug']}.html")

    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        links = "".join([f"<li><a href='{u}'>{u}</a></li>" for u in urls])
        f.write(f"<!doctype html><ul>{links}</ul>")

    print(f"Généré {len(urls)} pages !")

if __name__ == "__main__":
    main()

