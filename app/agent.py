# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import operator
import uuid
from typing import Optional

from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.cloud import firestore
from google.cloud import storage
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.instruction import INSTRUCTION

MODEL = "gemini-3.8-flash"
PROJECT_ID = "qwiklabs-gcp-04-deb6237d6161"
BUCKET_NAME = "baristabot-media-deb6237d6161"

# Firestore database client initialized with hardcoded project ID
db = firestore.Client(project=PROJECT_ID)
coffees_ref = db.collection("coffee_beans")

# Cloud Storage and GenAI clients for media and image generation
storage_client = storage.Client(project=PROJECT_ID)
media_bucket = storage_client.bucket(BUCKET_NAME)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")


def search_coffee_beans(query: str = "", roast_level: str = "", origin: str = "") -> str:
    """Search specialty coffee beans in the Firestore roastery database by name, flavor notes, origin, or roast level.

    Args:
        query: Free-text search term matching bean name, flavor notes, or description (e.g. 'jasmine', 'fruity', 'bourbon', 'chocolate').
        roast_level: Filter by roast level: 'Light', 'Medium-Light', 'Medium', or 'Dark'.
        origin: Filter by country of origin (e.g. 'Ethiopia', 'Colombia', 'Guatemala', 'Kenya', 'Indonesia').

    Returns:
        Formatted summary of matching coffee beans in stock.
    """
    try:
        docs = list(coffees_ref.stream())
        matches = []
        q_lower = query.lower().strip()
        r_lower = roast_level.lower().strip()
        o_lower = origin.lower().strip()

        for doc in docs:
            item = doc.to_dict()
            name = item.get("name", "")
            bean_origin = item.get("origin", "")
            roast = item.get("roast_level", "")
            notes = [n.lower() for n in item.get("flavor_notes", [])]
            desc = item.get("description", "").lower()

            if r_lower and r_lower not in roast.lower():
                continue
            if o_lower and o_lower not in bean_origin.lower():
                continue
            if q_lower:
                text_corpus = f"{name.lower()} {bean_origin.lower()} {' '.join(notes)} {desc}"
                if q_lower not in text_corpus:
                    continue

            matches.append(item)

        if not matches:
            return f"No coffee beans found matching query='{query}', roast='{roast_level}', origin='{origin}'."

        results = [f"Found {len(matches)} specialty coffee(s) in the roastery catalog:"]
        for b in matches:
            notes_str = ", ".join(b.get("flavor_notes", []))
            results.append(
                f"• [{b.get('id')}] {b.get('name')} | {b.get('origin')} ({b.get('process')} process)\n"
                f"  Roast: {b.get('roast_level')} | Notes: {notes_str} | Price: ${b.get('price_usd', 0):.2f}\n"
                f"  Best Brew: {b.get('recommended_brew')} (Temp: {b.get('water_temp_c')}°C, Ratio: {b.get('ratio')})"
            )
        return "\n\n".join(results)
    except Exception as e:
        return f"Error querying coffee beans database: {e}"


def get_coffee_details(bean_id: str) -> str:
    """Retrieve full details, origin story, and dial-in parameters for a specific coffee bean.

    Args:
        bean_id: Identifier of the coffee bean (e.g. 'ethiopia-yirgacheffe', 'colombia-huila-pink-bourbon').

    Returns:
        Detailed specifications and brewing guidance for the coffee bean.
    """
    try:
        doc = coffees_ref.document(bean_id.strip().lower()).get()
        if not doc.exists:
            # Try fuzzy search on name
            docs = list(coffees_ref.stream())
            for d in docs:
                data = d.to_dict()
                if bean_id.lower() in data.get("name", "").lower():
                    doc = d
                    break

        if not doc or not doc.exists:
            return f"Coffee bean with ID or name '{bean_id}' not found in catalog."

        b = doc.to_dict()
        notes = ", ".join(b.get("flavor_notes", []))
        return (
            f"=== {b.get('name')} ===\n"
            f"Origin: {b.get('origin')} ({b.get('region', 'Unknown Region')})\n"
            f"Elevation: {b.get('elevation_m', 'N/A')}m AMSL\n"
            f"Process: {b.get('process')}\n"
            f"Roast Level: {b.get('roast_level')}\n"
            f"Tasting Notes: {notes}\n"
            f"Price: ${b.get('price_usd', 0):.2f} (In Stock: {b.get('in_stock', True)})\n"
            f"Dial-in Recommendation:\n"
            f"  - Method: {b.get('recommended_brew')}\n"
            f"  - Grind Size: {b.get('recommended_grind')}\n"
            f"  - Water Temp: {b.get('water_temp_c')}°C ({int(b.get('water_temp_c', 92)*9/5+32)}°F)\n"
            f"  - Brew Ratio: {b.get('ratio')}\n"
            f"Description: {b.get('description', '')}"
        )
    except Exception as e:
        return f"Error retrieving coffee details: {e}"


def add_coffee_bean(
    name: str,
    origin: str,
    roast_level: str,
    process: str,
    flavor_notes: str,
    recommended_brew: str,
    price_usd: float,
    description: str = "",
) -> str:
    """Add a new specialty coffee bean to the Firestore roastery database.

    Args:
        name: Full name of the coffee (e.g. 'Costa Rica Tarrazu Geisha').
        origin: Country of origin (e.g. 'Costa Rica').
        roast_level: Roast degree ('Light', 'Medium-Light', 'Medium', 'Dark').
        process: Processing method ('Washed', 'Natural', 'Honey', 'Anaerobic').
        flavor_notes: Comma-separated tasting notes (e.g. 'Papaya, Jasmine, Lime').
        recommended_brew: Best brewing equipment (e.g. 'V60 Pour-over', 'AeroPress').
        price_usd: Price per 250g bag in USD.
        description: Short roaster notes or origin background.

    Returns:
        Confirmation message with the created document ID.
    """
    try:
        bean_id = name.lower().replace(" ", "-").replace("'", "").replace("/", "-")
        notes_list = [n.strip().title() for n in flavor_notes.split(",") if n.strip()]
        data = {
            "id": bean_id,
            "name": name,
            "origin": origin,
            "roast_level": roast_level,
            "process": process,
            "flavor_notes": notes_list,
            "recommended_brew": recommended_brew,
            "recommended_grind": "Medium-Fine",
            "water_temp_c": 92,
            "ratio": "1:16",
            "price_usd": float(price_usd),
            "in_stock": True,
            "description": description or f"{roast_level} roast {origin} coffee with notes of {flavor_notes}.",
        }
        coffees_ref.document(bean_id).set(data)
        return f"Successfully added '{name}' to Firestore (ID: {bean_id}) with {len(notes_list)} tasting notes."
    except Exception as e:
        return f"Error adding coffee bean to database: {e}"


def calculate_brew_recipe(brew_method: str, coffee_dose_grams: float = 15.0) -> str:
    """Calculate the precise brew recipe, water weight, bloom volume, and pour schedule for coffee gear.

    Args:
        brew_method: Brewing method or gear (e.g. 'v60', 'aeropress', 'french press', 'chemex', 'espresso', 'moka pot').
        coffee_dose_grams: Amount of ground coffee in grams (default 15.0g).

    Returns:
        Structured step-by-step brew guide with calculated weights and timings.
    """
    method = brew_method.lower().strip()
    dose = float(coffee_dose_grams)

    if "aeropress" in method:
        water = dose * 13.3
        bloom = dose * 3.0
        return (
            f"=== AeroPress Inverted Method Guide ===\n"
            f"• Coffee Dose: {dose:.1f}g (Medium-Fine grind)\n"
            f"• Water Amount: {water:.1f}g (~{water:.0f}ml) at 90°C (194°F)\n"
            f"• Brew Ratio: 1:13.3\n"
            f"Pour Schedule:\n"
            f"1. 0:00 - Pour {bloom:.0f}g water and stir 5 times. Let bloom for 30s.\n"
            f"2. 0:30 - Pour remainder up to {water:.0f}g. Stir gently.\n"
            f"3. 1:00 - Attach cap with rinsed filter, flip onto server.\n"
            f"4. 1:15 - Gently press for 30s until slight hiss at 1:45."
        )
    elif "v60" in method or "pour-over" in method or "pourover" in method:
        water = dose * 16.0
        bloom = dose * 3.0
        pour1 = (water - bloom) / 2
        return (
            f"=== Hario V60 Pour-Over Recipe ===\n"
            f"• Coffee Dose: {dose:.1f}g (Medium-Fine grind - table salt size)\n"
            f"• Total Water: {water:.1f}g at 93°C (200°F)\n"
            f"• Brew Ratio: 1:16\n"
            f"Pour Schedule:\n"
            f"1. 0:00 - Bloom with {bloom:.0f}g water. Swirl gently. Wait 45s.\n"
            f"2. 0:45 - First pour: add {pour1:.0f}g (reaching {bloom + pour1:.0f}g) in concentric circles.\n"
            f"3. 1:30 - Second pour: add {pour1:.0f}g (reaching {water:.0f}g total).\n"
            f"4. 2:00 - Give a gentle swirl. Target draw-down completes at 2:45 - 3:15."
        )
    elif "french" in method or "press" in method:
        water = dose * 15.0
        return (
            f"=== French Press Immersion Guide ===\n"
            f"• Coffee Dose: {dose:.1f}g (Coarse grind - sea salt size)\n"
            f"• Total Water: {water:.1f}g at 94°C (202°F)\n"
            f"• Brew Ratio: 1:15\n"
            f"Steps:\n"
            f"1. 0:00 - Add coffee and pour all {water:.0f}g water aggressively to saturate.\n"
            f"2. 4:00 - Break the crust with a spoon, scoop off excess foam/floating grounds.\n"
            f"3. 5:00 - Place plunger on top without pressing down. Let sediment settle until 8:00.\n"
            f"4. 8:00 - Press gently to surface of liquid and decant immediately."
        )
    elif "espresso" in method:
        yield_weight = dose * 2.0
        return (
            f"=== 9-Bar Espresso Extraction ===\n"
            f"• Dry Dose: {dose:.1f}g (Fine grind, WDT distribution, 30lb tamp)\n"
            f"• Target Yield: {yield_weight:.1f}g liquid espresso\n"
            f"• Brew Ratio: 1:2.0\n"
            f"• Water Temp: 93°C (200°F)\n"
            f"• Target Time: 26 - 30 seconds."
        )
    else:
        water = dose * 16.0
        return (
            f"=== General Pour-Over / Drip Guide ({brew_method}) ===\n"
            f"• Coffee Dose: {dose:.1f}g (Medium grind)\n"
            f"• Total Water: {water:.1f}g at 92°C (198°F)\n"
            f"• Standard Golden Cup Ratio: 1:16\n"
            f"• Bloom: {dose*2.5:.0f}g water for 45s, then steady continuous pours."
        )


async def generate_coffee_image(prompt: str, tool_context: ToolContext = None) -> str:
    """Generate specialty coffee images such as latte art designs, brewing steps, coffee cups, or origin landscapes using Gemini 3.1 Flash-Lite Image.

    Args:
        prompt: Detailed description of the visual coffee scene, latte art pattern, or brewing equipment (e.g. 'A ceramic cup with intricate swan latte art on glossy microfoam', 'A V60 pour over brewing setup with golden morning light').
        tool_context: Injected ADK ToolContext to register artifacts in the session.

    Returns:
        The public HTTPS URL of the uploaded image and a confirmation message.
    """
    try:
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        img_bytes = None
        mime_type = "image/jpeg"
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

        if not img_bytes:
            return "Error: No image was returned by the image generation model."

        filename = f"coffee_art_{uuid.uuid4().hex[:8]}.jpg"

        # 1. Save artifact for the ADK Playground Artifacts panel
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                artifact_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
                await tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as e:
                print(f"Warning saving artifact: {e}")

        # 2. Upload to public Cloud Storage bucket
        blob = media_bucket.blob(filename)
        blob.upload_from_string(img_bytes, content_type=mime_type)
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return f"Successfully generated coffee image!\nPublic URL: {public_url}\nArtifact: {filename}"
    except Exception as e:
        return f"Error generating image: {e}"


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    """After each turn, extract durable facts to the Vertex AI Memory Bank instance."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Warning in generate_memories_callback: {e}")
    return None

instruction = INSTRUCTION

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        search_coffee_beans,
        get_coffee_details,
        add_coffee_bean,
        calculate_brew_recipe,
        generate_coffee_image,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
