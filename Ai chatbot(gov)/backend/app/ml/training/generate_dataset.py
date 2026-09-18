"""
Generates a realistic synthetic complaint dataset with 1200+ records.
Covers 6 categories with formal, informal, and natural language variations.

Usage:
    python -m app.ml.training.generate_dataset
    OR
    python app/ml/training/generate_dataset.py
"""
import csv
import os
import random
from typing import List, Tuple

random.seed(42)

# ─── Template bank per category ───────────────────────────────────────────────

TEMPLATES = {
    "Water Supply": [
        "There has been no water supply in {location} for {duration}.",
        "Water supply is completely disrupted in our area since {duration}.",
        "No water coming from tap for {duration} in {location}.",
        "Water not coming from {duration}.",
        "Our entire street has been without water since {duration}.",
        "Water supply is interrupted daily in {location}.",
        "The pipeline near {location} is leaking and water is wasted.",
        "Dirty water is coming from the tap in {location}.",
        "Water is not supplied for {duration} and people are suffering.",
        "Water supply disruption affecting {location} colony.",
        "Low water pressure in {location} for the past {duration}.",
        "No potable water available in {location} ward.",
        "Drinking water pipeline broken near {location}.",
        "Water contamination noticed in {location} supply.",
        "Main water pipe burst on {location} road causing wastage.",
        "Ward {location} has been facing water shortage since {duration}.",
        "Water tanker not coming for {duration} to {location}.",
        "Irregular water supply in {location} residential area.",
        "No water in {location} apartment complex for {duration}.",
        "Pipeline leakage causing water logging in {location}.",
        "Public water tap not working in {location} for {duration}.",
        "Water meter damaged in {location} colony.",
        "Sewage water mixing with drinking water in {location}.",
        "Water supply cut without notice in {location} area.",
        "Hand pump not working in {location} for {duration}.",
    ],
    "Roads": [
        "The road near {location} has too many potholes.",
        "Road condition in {location} is very bad due to potholes.",
        "Many potholes on the main road in {location} causing accidents.",
        "Road repair needed urgently in {location}.",
        "The stretch of road near {location} is damaged and dangerous.",
        "Road surface broken in {location} after heavy rain.",
        "No proper road in {location} colony since {duration}.",
        "Road construction incomplete in {location} for {duration}.",
        "Footpath damaged near {location} causing inconvenience.",
        "Main road in {location} is waterlogged after rain.",
        "Speed breaker missing near school in {location}.",
        "Road divider broken on {location} highway.",
        "Digging work done on {location} road not filled properly.",
        "Bridge on {location} road is damaged and unsafe.",
        "Road markings faded on {location} road posing danger.",
        "Gravel road in {location} not paved causing dust.",
        "Road near {location} has large cracks and is sinking.",
        "Side road in {location} flooded due to poor drainage.",
        "Road not repaired for {duration} in {location}.",
        "Traffic island on {location} road is broken.",
        "Unauthorized construction blocking {location} road.",
        "Narrow road in {location} causing traffic jams.",
        "Road excavation by contractor in {location} not restored.",
        "Pot holes in {location} area destroying vehicles.",
        "Ring road near {location} damaged and needs resurfacing.",
    ],
    "Sanitation": [
        "Garbage has not been collected in {location} for {duration}.",
        "Garbage bins in {location} are overflowing.",
        "No sanitation service in our locality in {location}.",
        "Waste collection not done for {duration} in {location}.",
        "Dustbin near {location} is full and not cleared for {duration}.",
        "Dead animals lying on road in {location} creating health hazard.",
        "Open garbage dumped near {location} park.",
        "Sweeper has not visited {location} for {duration}.",
        "Public toilet near {location} is very dirty and needs cleaning.",
        "Garbage vehicle not coming to {location} since {duration}.",
        "Waste burning happening near {location} affecting air quality.",
        "Littering problem on {location} beach area.",
        "No dustbins provided in {location} market area.",
        "Garbage pile near {location} hospital entrance.",
        "Solid waste management failure in {location} ward.",
        "Sewage smell coming from {location} street.",
        "Open defecation near {location} because of no toilet.",
        "Unhygienic conditions in {location} market due to garbage.",
        "Street dogs attacking due to garbage at {location}.",
        "Waste segregation not done by staff in {location}.",
        "Garbage truck route skipping {location} area.",
        "Industrial waste illegally dumped near {location}.",
        "Construction debris not removed from {location} for {duration}.",
        "Bio-medical waste dumped near {location} road.",
        "Public places dirty due to no sweeping in {location}.",
    ],
    "Electricity": [
        "There is no electricity supply in {location} since {duration}.",
        "Power cuts happening frequently in {location}.",
        "Electricity supply disrupted for {duration} in {location}.",
        "Power failure in {location} since {duration} causing problems.",
        "No power supply to {location} area for {duration}.",
        "Frequent power outages in {location} colony.",
        "Transformer blown in {location} area since {duration}.",
        "Electric wire hanging low on {location} road dangerous.",
        "Electricity bill is incorrect for connection in {location}.",
        "Meter not working properly at {location}.",
        "Power supply quality poor with low voltage in {location}.",
        "Electricity restored but flickering continuously in {location}.",
        "Substation fault causing outage in {location} for {duration}.",
        "Loose electric wire on road near {location} is dangerous.",
        "Power supply cut without prior notice in {location}.",
        "Load shedding scheduled but not notified to {location} residents.",
        "Electric pole damaged near {location} road.",
        "Cable theft causing power outage in {location}.",
        "High voltage sparks from wire near {location}.",
        "New electricity connection not provided in {location} for {duration}.",
        "Electricity meter tampered in {location} apartment.",
        "Fuse box damaged in {location} locality.",
        "Power disruption causing losses to businesses in {location}.",
        "Overhead cable broken and lying on road in {location}.",
        "Transformer noise disturbing residents of {location}.",
    ],
    "Street Lighting": [
        "Street lights not working in {location} for {duration}.",
        "Street light near {location} is not functioning since {duration}.",
        "Dark roads in {location} due to non-working street lights.",
        "Several street lights off on {location} road for {duration}.",
        "No street lighting in {location} causing safety issues.",
        "Street light pole broken near {location}.",
        "Street lights on {location} road are dim and not enough.",
        "All street lights in {location} area are off since {duration}.",
        "Women feel unsafe walking on {location} due to no street lights.",
        "Accidents happening on {location} road due to no lighting.",
        "Street light cable stolen in {location} colony.",
        "Damaged street light post on {location} road.",
        "New streets in {location} have no street light installed.",
        "Street lights remain ON during daytime in {location} wasting electricity.",
        "Flickering street light near {location} disturbing residents.",
        "Street light timer malfunction in {location} ward.",
        "LED street light needs replacement in {location}.",
        "No light near {location} bus stop causing issues.",
        "Park in {location} has no lighting making it unsafe.",
        "Street lamp broken near {location} school.",
        "Vandalism of street light in {location} colony.",
        "New colony {location} not provided with street lights.",
        "Solar street lights not working in {location} for {duration}.",
        "Street light reports pending for {duration} in {location}.",
        "Entire {location} area dark at night due to power failure.",
    ],
    "Drainage": [
        "Drain near {location} is blocked and water is overflowing.",
        "Drainage system in {location} is choked and needs cleaning.",
        "Sewage overflowing on road in {location}.",
        "Drain not cleaned in {location} for {duration} causing flooding.",
        "Water logging in {location} due to blocked drainage.",
        "Sewage water on road in {location} creating unhygienic conditions.",
        "Open drain in {location} causing mosquito breeding.",
        "Main drain in {location} blocked after heavy rain.",
        "Drainage water entering homes in {location}.",
        "Stormwater drain not maintained in {location} for {duration}.",
        "Bad smell from drain near {location}.",
        "Sewer line broken near {location} causing leakage.",
        "Water standing in {location} for {duration} due to poor drainage.",
        "Manhole open in {location} road is dangerous.",
        "Drainage canal blocked near {location} bridge.",
        "Septic tank overflow in {location} colony.",
        "Drain not cleaned before monsoon in {location}.",
        "Flooding in {location} due to inadequate drainage.",
        "Drain outlet blocked in {location} causing backflow.",
        "Sewage pumping station failed in {location}.",
        "Open sewer near {location} market causing health risk.",
        "Underground drainage choked in {location} for {duration}.",
        "Drainage work done but not completed in {location}.",
        "Nala near {location} encroached blocking water flow.",
        "Rainwater harvesting pit blocked near {location}.",
    ],
}

LOCATIONS = [
    "Ward 5", "Ward 12", "Ward 7", "Gandhi Nagar", "Rajampet",
    "MG Road", "Station Road", "RTC Bus Stand", "Market Area",
    "Nehru Colony", "Ambedkar Nagar", "Srinivasa Nagar", "Old Town",
    "New Town", "Lakshmi Puram", "Ramaiah Street", "Indira Nagar",
    "Patel Nagar", "Anna Nagar", "Bose Nagar", "Ashok Nagar",
    "Bhagath Singh Nagar", "near government hospital", "near school",
    "near railway station", "main junction", "outer ring road",
    "Jubilee Hills", "Dilsukhnagar", "Kukatpally", "Ameerpet",
    "Begumpet", "Himayatnagar", "ECIL", "Uppal", "LB Nagar",
]

DURATIONS = [
    "2 days", "3 days", "5 days", "1 week", "10 days",
    "2 weeks", "a month", "several days", "Monday", "last week",
    "yesterday", "4 days", "7 days", "more than a week", "15 days",
    "last Tuesday", "3 months", "2 months", "since last month",
]

PRIORITY_FEATURES = {
    "Water Supply": {
        "High": ["no water", "water not coming", "no water supply", "disrupted", "shortage",
                 "pipeline broken", "contamination", "sewage mixing"],
        "Critical": ["sewage mixing with drinking water", "water contamination", "health hazard",
                     "pipeline burst", "flood", "water logging"],
        "Medium": ["low pressure", "irregular", "water tanker"],
        "Low": ["meter damaged", "billing issue"],
    },
    "Roads": {
        "High": ["accident", "dangerous", "unsafe", "bridge damaged", "sinking"],
        "Critical": ["bridge collapse", "major accident", "life risk"],
        "Medium": ["potholes", "damaged road", "not repaired"],
        "Low": ["footpath", "road markings", "narrow"],
    },
    "Sanitation": {
        "High": ["overflowing", "health hazard", "dead animals", "hospital", "bio-medical"],
        "Critical": ["epidemic", "disease outbreak", "toxic waste"],
        "Medium": ["garbage not collected", "sweeper not coming", "dirty"],
        "Low": ["no dustbin", "littering"],
    },
    "Electricity": {
        "High": ["no electricity", "power failure", "transformer blown", "wire dangerous"],
        "Critical": ["electric wire on road", "sparks", "electrocution risk", "fire hazard"],
        "Medium": ["frequent outage", "low voltage", "power cuts"],
        "Low": ["billing issue", "meter not working", "noise"],
    },
    "Street Lighting": {
        "High": ["women unsafe", "accidents", "dark road", "no lighting", "dangerous"],
        "Critical": ["accident happened", "assault", "crime"],
        "Medium": ["lights not working", "several lights off", "dim lights"],
        "Low": ["flickering", "lights on in daytime", "timer malfunction"],
    },
    "Drainage": {
        "High": ["flooding", "sewage overflowing", "water entering homes", "open manhole"],
        "Critical": ["houses flooded", "health emergency", "disease"],
        "Medium": ["blocked drain", "water logging", "bad smell"],
        "Low": ["drain not cleaned", "mosquito breeding"],
    },
}


def assign_priority(text: str, category: str) -> str:
    """Rule-based priority for dataset generation (NOT used in production prediction)."""
    text_lower = text.lower()
    features = PRIORITY_FEATURES.get(category, {})
    for level in ["Critical", "High", "Medium", "Low"]:
        for kw in features.get(level, []):
            if kw in text_lower:
                return level
    return "Medium"


def generate_record(category: str) -> Tuple[str, str, str, str]:
    """Generate a single complaint record."""
    templates = TEMPLATES[category]
    template = random.choice(templates)
    location = random.choice(LOCATIONS)
    duration = random.choice(DURATIONS)
    text = template.format(location=location, duration=duration)
    priority = assign_priority(text, category)
    return text, category, priority, location


def generate_dataset(n_per_category: int = 200, output_path: str = None) -> List[dict]:
    """
    Generate a balanced dataset with n_per_category samples per category.
    Default: 200 × 6 = 1200 records.
    """
    categories = list(TEMPLATES.keys())
    records = []

    for category in categories:
        generated = set()
        count = 0
        attempts = 0
        while count < n_per_category and attempts < n_per_category * 10:
            attempts += 1
            text, cat, priority, location = generate_record(category)
            # Add small variations to avoid exact duplicates
            variations = [
                text,
                text.replace(".", "!"),
                text.lower(),
                text.replace("the ", "").replace("The ", ""),
            ]
            chosen = random.choice(variations)
            if chosen not in generated:
                generated.add(chosen)
                records.append({
                    "text": chosen,
                    "category": cat,
                    "priority": priority,
                    "location": location,
                })
                count += 1

    random.shuffle(records)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "category", "priority", "location"])
            writer.writeheader()
            writer.writerows(records)
        print(f"[OK] Dataset saved to {output_path} ({len(records)} records)")

    return records


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    output = os.path.join("data", "complaints.csv")
    records = generate_dataset(n_per_category=200, output_path=output)
    print(f"\nCategory distribution:")
    from collections import Counter
    cats = Counter(r["category"] for r in records)
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    print(f"\nPriority distribution:")
    pris = Counter(r["priority"] for r in records)
    for pri, count in sorted(pris.items()):
        print(f"  {pri}: {count}")
