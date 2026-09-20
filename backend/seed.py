import os
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from backend.database import SessionLocal, Base, engine, BASE_DIR
from backend.models import FoundItem, LostReport

DATA_DIR = os.path.join(BASE_DIR, "data")
SEED_DIR = os.path.join(DATA_DIR, "seed")
IMAGES_DIR = os.path.join(SEED_DIR, "images")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

os.makedirs(SEED_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


def create_synthetic_image(filename: str, bg_color: tuple, shape_type: str, fg_color: tuple, label: str) -> str:
    """Generate a clean visual representation for seed items to test CLIP embeddings."""
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        return filepath

    img = Image.new("RGB", (400, 400), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw simple representative shapes
    if shape_type == "backpack":
        # Draw backpack silhouette
        draw.rounded_rectangle([(100, 90), (300, 340)], radius=35, fill=fg_color, outline=(40, 40, 50), width=4)
        draw.rounded_rectangle([(130, 190), (270, 310)], radius=15, fill=(fg_color[0] + 20, fg_color[1] + 20, min(255, fg_color[2] + 20)), outline=(30, 30, 40), width=3)
        draw.arc([(150, 40), (250, 110)], start=180, end=0, fill=(30, 30, 30), width=10)
    elif shape_type == "laptop":
        # Draw open laptop
        draw.polygon([(80, 260), (320, 260), (350, 330), (50, 330)], fill=fg_color, outline=(30, 30, 30))
        draw.rounded_rectangle([(95, 110), (305, 260)], radius=10, fill=(20, 25, 35), outline=(50, 50, 60), width=4)
        draw.rectangle([(110, 125), (290, 245)], fill=(70, 130, 180))
    elif shape_type == "watch":
        # Draw watch
        draw.rectangle([(170, 40), (230, 360)], fill=(40, 30, 20), outline=(20, 15, 10), width=2)
        draw.ellipse([(120, 120), (280, 280)], fill=fg_color, outline=(30, 30, 30), width=5)
        draw.ellipse([(140, 140), (260, 260)], fill=(250, 250, 245), outline=(100, 100, 100), width=2)
        draw.line([(200, 200), (200, 160)], fill=(20, 20, 20), width=4)
        draw.line([(200, 200), (235, 200)], fill=(20, 20, 20), width=3)
    elif shape_type == "suitcase":
        # Draw rolling luggage
        draw.rounded_rectangle([(110, 100), (290, 340)], radius=20, fill=fg_color, outline=(20, 30, 50), width=4)
        draw.rectangle([(130, 120), (270, 320)], fill=(fg_color[0] + 15, fg_color[1] + 15, min(255, fg_color[2] + 15)))
        draw.rectangle([(170, 40), (230, 100)], fill=None, outline=(50, 50, 50), width=6)
        draw.ellipse([(125, 335), (155, 365)], fill=(30, 30, 30))
        draw.ellipse([(245, 335), (275, 365)], fill=(30, 30, 30))
    elif shape_type == "bottle":
        # Draw water bottle
        draw.rounded_rectangle([(150, 100), (250, 350)], radius=25, fill=fg_color, outline=(40, 20, 20), width=3)
        draw.rectangle([(175, 50), (225, 100)], fill=(180, 180, 190), outline=(60, 60, 60), width=2)
    elif shape_type == "wallet":
        # Draw leather wallet
        draw.rounded_rectangle([(80, 130), (320, 280)], radius=15, fill=fg_color, outline=(30, 20, 10), width=4)
        draw.line([(80, 205), (320, 205)], fill=(40, 25, 15), width=2)
        draw.rectangle([(260, 185), (300, 225)], fill=(180, 150, 50), outline=(50, 40, 10), width=2)
    elif shape_type == "headphones":
        # Draw headphones
        draw.arc([(100, 70), (300, 270)], start=180, end=0, fill=(40, 40, 40), width=16)
        draw.rounded_rectangle([(80, 190), (135, 290)], radius=20, fill=fg_color, outline=(20, 20, 20), width=3)
        draw.rounded_rectangle([(265, 190), (320, 290)], radius=20, fill=fg_color, outline=(20, 20, 20), width=3)
    else:
        draw.rectangle([(100, 100), (300, 300)], fill=fg_color, outline=(30, 30, 30), width=3)

    # Add text label badge
    draw.rectangle([(20, 365), (380, 395)], fill=(20, 20, 20))
    draw.text((30, 372), label, fill=(240, 240, 240))

    img.save(filepath, "JPEG", quality=90)
    return filepath


def generate_seed_images():
    """Create realistic seed images."""
    create_synthetic_image("found_navy_backpack.jpg", (230, 235, 240), "backpack", (25, 45, 95), "Found: Navy Blue Backpack")
    create_synthetic_image("lost_black_rucksack.jpg", (225, 230, 235), "backpack", (35, 45, 65), "Lost: Dark Rucksack")

    create_synthetic_image("found_silver_laptop.jpg", (240, 240, 245), "laptop", (180, 185, 195), "Found: Silver Ultrabook")
    create_synthetic_image("lost_grey_laptop.jpg", (235, 235, 240), "laptop", (130, 135, 145), "Lost: Grey Aluminum Laptop")

    create_synthetic_image("found_gold_watch.jpg", (245, 245, 235), "watch", (215, 165, 45), "Found: Gold Chronograph Watch")
    # Note: Lost watch deliberately has NO photo to test missing photo re-normalization

    create_synthetic_image("found_blue_suitcase.jpg", (235, 240, 245), "suitcase", (30, 85, 160), "Found: Blue Rolling Suitcase")
    create_synthetic_image("lost_blue_suitcase.jpg", (230, 235, 240), "suitcase", (40, 95, 175), "Lost: Blue Travel Luggage")

    create_synthetic_image("found_red_bottle.jpg", (245, 235, 235), "bottle", (190, 35, 40), "Found: Red Insulated Flask")
    create_synthetic_image("lost_red_bottle.jpg", (240, 230, 230), "bottle", (170, 30, 35), "Lost: Crimson Thermos Flask")

    create_synthetic_image("found_brown_wallet.jpg", (245, 240, 230), "wallet", (110, 65, 30), "Found: Brown Leather Wallet")
    create_synthetic_image("lost_brown_wallet.jpg", (240, 235, 225), "wallet", (125, 75, 40), "Lost: Tan Pocket Billfold")

    create_synthetic_image("found_black_headphones.jpg", (235, 235, 235), "headphones", (30, 30, 35), "Found: Black ANC Headphones")
    create_synthetic_image("lost_black_headphones.jpg", (230, 230, 230), "headphones", (45, 45, 50), "Lost: Wireless Over-Ear Headset")


def seed_database(db: Session, force: bool = False):
    """Seed the database with standard 7 found items and 7 lost reports."""
    generate_seed_images()

    existing_found = db.query(FoundItem).count()
    if existing_found > 0 and not force:
        print(f"[TRACE] Database already seeded with {existing_found} found items.")
        return

    # Clear existing if force
    if force:
        db.query(FoundItem).delete()
        db.query(LostReport).delete()
        db.commit()

    now = datetime.utcnow()

    # 7 Seed Found Items
    found_items_data = [
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_navy_backpack.jpg"),
            "description": "Navy blue canvas backpack with leather bottom and padded shoulder straps",
            "location": "Platform 4",
            "found_at": now - timedelta(hours=5),
            "hidden_attribute": "small tear on the left strap with yellow lining inside front pocket",
            "key_terms": "tear, left strap, yellow lining",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_silver_laptop.jpg"),
            "description": "Silver metallic ultraportable notebook computer in grey zip sleeve",
            "location": "Waiting Hall",
            "found_at": now - timedelta(days=1, hours=3),
            "hidden_attribute": "scratch on bottom casing and green Python sticker near trackpad",
            "key_terms": "python sticker, scratch, bottom casing",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_gold_watch.jpg"),
            "description": "Gold wrist chronograph with black leather strap and white dial",
            "location": "Near Ticket Counter",
            "found_at": now - timedelta(days=2),
            "hidden_attribute": "engraved anniversary date 14-02-2018 on rear case plate",
            "key_terms": "engraved, 2018, anniversary, 14-02-2018",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_blue_suitcase.jpg"),
            "description": "Blue hard-shell rolling suitcase with 4 spinner wheels and retractable handle",
            "location": "Main Concourse",
            "found_at": now - timedelta(hours=18),
            "hidden_attribute": "airline baggage tag with initials R.S. on top handle",
            "key_terms": "r.s., baggage tag, initials, r s",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_red_bottle.jpg"),
            "description": "Red insulated stainless steel water flask 750ml with loop cap",
            "location": "Food Court",
            "found_at": now - timedelta(days=3),
            "hidden_attribute": "dent on bottom rim and faded sticker of a mountain peak",
            "key_terms": "dent, mountain sticker, bottom rim",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_brown_wallet.jpg"),
            "description": "Brown bi-fold genuine leather wallet with brass snap coin pocket",
            "location": "Platform 2",
            "found_at": now - timedelta(hours=8),
            "hidden_attribute": "metro transit smartcard expiring 2027 and silver lucky coin inside",
            "key_terms": "metro smartcard, transit card, lucky coin, 2027",
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "found_black_headphones.jpg"),
            "description": "Wireless noise-cancelling overhead headphones in black zip clamshell case",
            "location": "Coach B4",
            "found_at": now - timedelta(days=4),
            "hidden_attribute": "custom red replacement ear cushions and coiled charging cable",
            "key_terms": "red ear cushions, red cushions, coiled cable",
            "status": "open",
        },
    ]

    # 7 Seed Lost Reports
    lost_reports_data = [
        {
            # Mismatched wording with Item 1: "black rucksack" vs "navy blue canvas backpack"
            "photo_path": os.path.join(IMAGES_DIR, "lost_black_rucksack.jpg"),
            "description": "Black rucksack with dual straps and side mesh pocket",
            "location": "Near Ticket Counter",
            "lost_at": now - timedelta(hours=7),
            "status": "open",
        },
        {
            # Mismatched wording with Item 2: "dark grey aluminum laptop" vs "silver ultraportable notebook"
            "photo_path": os.path.join(IMAGES_DIR, "lost_grey_laptop.jpg"),
            "description": "Dark grey aluminum laptop pc inside padded case",
            "location": "Waiting Hall",
            "lost_at": now - timedelta(days=1, hours=5),
            "status": "open",
        },
        {
            # No photo test with Item 3:
            "photo_path": None,
            "description": "Yellow metal analog watch with dark band and chronograph dials",
            "location": "Main Concourse",
            "lost_at": now - timedelta(days=2, hours=4),
            "status": "open",
        },
        {
            # For false claim / true claim verification with Item 4:
            "photo_path": os.path.join(IMAGES_DIR, "lost_blue_suitcase.jpg"),
            "description": "Blue travel suitcase hard luggage with four wheels",
            "location": "Platform 3",
            "lost_at": now - timedelta(days=1),
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "lost_red_bottle.jpg"),
            "description": "Crimson thermos metal drink bottle with screw top",
            "location": "Cafeteria",
            "lost_at": now - timedelta(days=3, hours=2),
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "lost_brown_wallet.jpg"),
            "description": "Tan pocket billfold with card slots and cash compartment",
            "location": "Platform 1",
            "lost_at": now - timedelta(hours=10),
            "status": "open",
        },
        {
            "photo_path": os.path.join(IMAGES_DIR, "lost_black_headphones.jpg"),
            "description": "Over-ear bluetooth audio headset with protective case",
            "location": "Platform 4",
            "lost_at": now - timedelta(days=4, hours=6),
            "status": "open",
        },
    ]

    # Save to JSON files as required by Section 8
    with open(os.path.join(SEED_DIR, "found_items.json"), "w", encoding="utf-8") as f:
        # Convert datetimes to ISO
        json.dump([{**item, "found_at": item["found_at"].isoformat()} for item in found_items_data], f, indent=2)

    with open(os.path.join(SEED_DIR, "lost_reports.json"), "w", encoding="utf-8") as f:
        json.dump([{**report, "lost_at": report["lost_at"].isoformat()} for report in lost_reports_data], f, indent=2)

    # Insert into SQLite
    for item in found_items_data:
        db.add(FoundItem(**item))
    for report in lost_reports_data:
        db.add(LostReport(**report))

    db.commit()
    print(f"[TRACE] Successfully seeded database with {len(found_items_data)} found items and {len(lost_reports_data)} lost reports.")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
