import html
import json
import re
from pathlib import Path

from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
OUTPUT = ROOT / "data" / "character_details.json"

ROLE = {"Attacker": "공격", "Supporter": "지원", "Breaker": "버스터", "Defender": "수호"}
ELEMENT = {"Dark": "어둠", "Fire": "불", "Water": "물", "Wind": "바람", "Earth": "대지", "Light": "성", "Physical": "물리"}
WEAPON = {
    "Gauntlets": "건틀릿", "Two-hand Sword": "양손검", "Axe": "도끼", "Sword": "한손검",
    "Dual Swords": "쌍검", "Staff": "스태프", "Wand": "완드", "Tome": "마도서",
    "Book": "마도서", "Lance": "랜스", "Spear": "창", "Rapier": "레이피어",
    "Shield": "방패", "Dagger": "단검", "Bow": "활"
}


def clean(value: str) -> str:
    return html.unescape(re.sub(r"\\(.)", r"\1", value)).strip()


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    characters = [r for r in catalog["records"] if r["category"] == "characters"]
    output = {"generated_at": catalog.get("generated_at", ""), "characters": {}}
    for record in characters:
        url = f"https://7dsorigin.app/en/characters/{record['slug']}"
        request = Request(url, headers={"User-Agent": "7DSOriginCompleteGuide/1.1"})
        page = urlopen(request, timeout=30).read().decode("utf-8")
        meta = re.search(r'<meta name="description" content="([^"]+)"', page)
        variants = []
        seen = set()
        for weapon, role, element in re.findall(r'title=\\?"([^"•]+) • ([^"•]+) • ([^"•]+)\\?"', page):
            key = (clean(weapon), clean(role), clean(element))
            if key in seen:
                continue
            seen.add(key)
            variants.append({
                "weapon": WEAPON.get(key[0], key[0]), "weapon_en": key[0],
                "role": ROLE.get(key[1], key[1]), "role_en": key[1],
                "element": ELEMENT.get(key[2], key[2]), "element_en": key[2]
            })
        output["characters"][record["slug"]] = {
            "name_ko": record["name_ko"], "name_en": record["name_en"],
            "description_ko": record.get("description_ko", ""),
            "description_en": clean(meta.group(1)) if meta else record.get("description_en", ""),
            "portrait_url": record.get("image_url", ""),
            "banner_url": f"https://7dsorigin.app/images/characters/banners/{record['slug']}.webp",
            "source_url": url, "variants": variants
        }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {len(output['characters'])} characters to {OUTPUT}")


if __name__ == "__main__":
    main()
