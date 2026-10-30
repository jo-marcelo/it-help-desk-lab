"""Build simulator/index.html from app.template.html, config.json and scenarios/*.json.

A published claude.ai page has to be one self-contained file, so this script
checks every scenario against config.json and embeds them all in the page.
Run it after adding or editing a scenario:  python build.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
CATEGORIES = ("diagnosis", "verification", "communication", "documentation")
AUTO_CHECKS = {"category", "final_status", "assigned_group"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(s, config):
    errors = []
    sid = s.get("id", "?")
    action_ids = {a["id"] for a in config["actions"]}
    if s.get("priority") not in config["priorities"]:
        errors.append(f"{sid}: unknown priority {s.get('priority')}")
    for aid in s["solution"]["actions"]:
        if aid not in action_ids:
            errors.append(f"{sid}: unknown action {aid}")
    for m in s["solution"]["accepted_verification"]:
        if m not in config["verification_methods"]:
            errors.append(f"{sid}: unknown verification method {m}")
    exp = s["expected_ticket"]
    if exp["category"] not in config["categories"]:
        errors.append(f"{sid}: unknown category {exp['category']}")
    if exp["final_status"] not in config["statuses"]:
        errors.append(f"{sid}: unknown status {exp['final_status']}")
    if exp["assigned_group"] not in config["groups"]:
        errors.append(f"{sid}: unknown group {exp['assigned_group']}")
    for cat in CATEGORIES:
        checks = s["rubric"].get(cat, [])
        total = sum(c["points"] for c in checks)
        if total != 25:
            errors.append(f"{sid}: {cat} checks add up to {total}, not 25")
        for c in checks:
            if "auto" in c and c["auto"] not in AUTO_CHECKS:
                errors.append(f"{sid}: unknown auto check {c['auto']}")
    return errors


def main():
    config = load(ROOT / "config.json")
    scenarios = [load(p) for p in sorted((ROOT / "scenarios").glob("*.json"))]
    errors = [e for s in scenarios for e in validate(s, config)]
    if errors:
        print("\n".join(errors))
        sys.exit(1)

    def embed(data):
        return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    page = (ROOT / "app.template.html").read_text(encoding="utf-8")
    page = page.replace("__CONFIG__", embed(config)).replace("__SCENARIOS__", embed(scenarios))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"Built index.html with {len(scenarios)} scenarios")


if __name__ == "__main__":
    main()
