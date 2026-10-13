#!/usr/bin/env python3
"""Seed Firestore collection 'coffee_beans' for BaristaBot."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-deb6237d6161"

COFFEE_DATA = [
    {
        "id": "ethiopia-yirgacheffe",
        "name": "Ethiopia Yirgacheffe G1",
        "origin": "Ethiopia",
        "region": "Yirgacheffe, Gedeb",
        "roast_level": "Light",
        "process": "Washed",
        "flavor_notes": ["Jasmine", "Bergamot", "Peach", "Earl Grey"],
        "recommended_brew": "V60 Pour-over",
        "recommended_grind": "Medium-Fine",
        "water_temp_c": 93,
        "ratio": "1:16",
        "elevation_m": 2100,
        "price_usd": 21.00,
        "in_stock": True,
        "description": "Floral and intensely aromatic with silky stone fruit and black tea notes.",
    },
    {
        "id": "colombia-huila-pink-bourbon",
        "name": "Colombia Huila Pink Bourbon",
        "origin": "Colombia",
        "region": "Huila, Pitalito",
        "roast_level": "Medium-Light",
        "process": "Honey",
        "flavor_notes": ["Pink Grapefruit", "Honey", "Red Currant", "Panela"],
        "recommended_brew": "AeroPress",
        "recommended_grind": "Medium",
        "water_temp_c": 91,
        "ratio": "1:15",
        "elevation_m": 1850,
        "price_usd": 23.50,
        "in_stock": True,
        "description": "Juicy and vibrant rare varietal bursting with tropical sweetness and bright acidity.",
    },
    {
        "id": "guatemala-antigua-los-volcanes",
        "name": "Guatemala Antigua Los Volcanes",
        "origin": "Guatemala",
        "region": "Antigua Valley",
        "roast_level": "Medium",
        "process": "Washed",
        "flavor_notes": ["Milk Chocolate", "Toasted Almond", "Orange Peel", "Caramel"],
        "recommended_brew": "Espresso",
        "recommended_grind": "Fine",
        "water_temp_c": 92,
        "ratio": "1:2 (Espresso)",
        "elevation_m": 1650,
        "price_usd": 18.00,
        "in_stock": True,
        "description": "Rich volcanic soil produces a classic balanced cup with velvety chocolate body.",
    },
    {
        "id": "kenya-nyeri-hill-aa",
        "name": "Kenya Nyeri Hill AA",
        "origin": "Kenya",
        "region": "Nyeri County",
        "roast_level": "Light",
        "process": "Washed",
        "flavor_notes": ["Blackcurrant", "Grapefruit", "Cane Sugar", "Tomato Vine"],
        "recommended_brew": "V60 Pour-over",
        "recommended_grind": "Medium-Fine",
        "water_temp_c": 94,
        "ratio": "1:16.5",
        "elevation_m": 1900,
        "price_usd": 22.00,
        "in_stock": True,
        "description": "Bold, dynamic phosphoric acidity and trademark Kenyan deep berry complexity.",
    },
    {
        "id": "sumatra-mandheling-triple-picked",
        "name": "Sumatra Mandheling Triple Picked",
        "origin": "Indonesia",
        "region": "Aceh, Lake Toba",
        "roast_level": "Dark",
        "process": "Wet-Hulled (Giling Basah)",
        "flavor_notes": ["Dark Chocolate", "Cedar", "Molasses", "Earthy Spice"],
        "recommended_brew": "French Press",
        "recommended_grind": "Coarse",
        "water_temp_c": 89,
        "ratio": "1:14",
        "elevation_m": 1400,
        "price_usd": 17.50,
        "in_stock": True,
        "description": "Full-bodied, syrupy, low-acidity dark roast with herbaceous earthy richness.",
    },
]

def seed():
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("coffee_beans")
    print(f"Connecting to Firestore for project {PROJECT_ID}...")
    for item in COFFEE_DATA:
        doc_id = item["id"]
        collection.document(doc_id).set(item)
        print(f"  ✓ Seeded: {item['name']} ({doc_id})")
    print("Firestore seeding complete!")

if __name__ == "__main__":
    seed()
