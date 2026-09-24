"""KrishiSetu AI - PlantVillage Class Registry & Metadata.

This module catalogues the 38 official classes from the PlantVillage dataset,
providing structured parsing of folder names and agricultural metadata
(crop, pathogen condition, health status, pathogen category, and cultural advisory).
"""

from typing import Dict, Any, List

# Complete mapping of the 38 official PlantVillage dataset classes
PLANTVILLAGE_CLASSES: List[str] = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Targeted non-blanket agronomic advisory lookup keyed by raw class name
CLASS_METADATA: Dict[str, Dict[str, Any]] = {
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "condition": "Late Blight",
        "pathogen_type": "oomycete / fungal-like",
        "is_healthy": False,
        "favorable_weather": "Cool (15-22°C) with persistent high humidity (>85%) and wet foliage",
        "targeted_guidance": "Prune severely infected lower foliage to reduce spore load. Improve inter-plant airflow and drip-irrigate at base to prevent leaf wetness. Avoid overhead sprinkler irrigation."
    },
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "condition": "Early Blight",
        "pathogen_type": "fungal",
        "is_healthy": False,
        "favorable_weather": "Warm (24-30°C) with alternating wet and dry periods",
        "targeted_guidance": "Remove and destroy affected lower leaves with concentric rings. Stake plants to elevate leaves off soil. Mulch heavily to prevent rain splash."
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "condition": "Bacterial Spot",
        "pathogen_type": "bacterial",
        "is_healthy": False,
        "favorable_weather": "Warm (24-30°C) accompanied by driving rain or overhead watering",
        "targeted_guidance": "Do not work in the field while plants are wet. Sanitize pruning shears between plants. Rogue out severely stunted seedlings."
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "condition": "Leaf Mold",
        "pathogen_type": "fungal",
        "is_healthy": False,
        "favorable_weather": "High relative humidity (>85%) and moderate warmth (21-24°C)",
        "targeted_guidance": "Improve greenhouse/canopy ventilation. Thin dense canopy shoots to enhance horizontal breeze circulation."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "condition": "Septoria Leaf Spot",
        "pathogen_type": "fungal",
        "is_healthy": False,
        "favorable_weather": "Warm, humid weather with frequent rain showers",
        "targeted_guidance": "Remove first-spotted basal leaves. Ensure 3-year crop rotation away from solanaceous species (potato/eggplant)."
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "condition": "Two-spotted Spider Mite",
        "pathogen_type": "mite / pest",
        "is_healthy": False,
        "favorable_weather": "Hot (>30°C) and arid / low-humidity environments",
        "targeted_guidance": "Inspect undersides of leaves for fine webbing. Introduce predatory mites (Phytoseiidae) or apply targeted neem-based biological oil in early morning."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "condition": "Target Spot",
        "pathogen_type": "fungal",
        "is_healthy": False,
        "favorable_weather": "Warm, humid tropical and sub-tropical conditions",
        "targeted_guidance": "Maintain wide row spacing to facilitate leaf drying. Avoid excess nitrogen fertilization which promotes lush, vulnerable foliage."
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "condition": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen_type": "viral (vectored by Bemisia tabaci whiteflies)",
        "is_healthy": False,
        "favorable_weather": "Warm, dry conditions supporting whitefly proliferation",
        "targeted_guidance": "Eradicate whitefly vector populations using yellow sticky traps and reflective silver mulches. Immediately remove and destroy symptomatic stunted plants."
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "condition": "Tomato Mosaic Virus (ToMV)",
        "pathogen_type": "viral (mechanically transmitted)",
        "is_healthy": False,
        "favorable_weather": "Spread via mechanical contact during pruning and staking",
        "targeted_guidance": "Wash hands with skim milk or soap solution before handling plants. Destroy infected plants immediately; do not compost."
    },
    "Tomato___healthy": {
        "crop": "Tomato",
        "condition": "Healthy Foliage",
        "pathogen_type": "none",
        "is_healthy": True,
        "favorable_weather": "Optimal growing conditions",
        "targeted_guidance": "Maintain balanced nutrition and regular field monitoring. No chemical or intervention action needed."
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "condition": "Early Blight",
        "pathogen_type": "fungal",
        "is_healthy": False,
        "favorable_weather": "Warm (24-29°C) with heavy dew or frequent rain",
        "targeted_guidance": "Hill soil properly around potato tubers. Avoid excessive nitrogen late in season. Destroy volunteer potato foliage."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "condition": "Late Blight",
        "pathogen_type": "oomycete / fungal-like",
        "is_healthy": False,
        "favorable_weather": "Cool (10-20°C) with persistent fog, cloud cover, or heavy rainfall (>90% humidity)",
        "targeted_guidance": "Urgent notification: inspect all surrounding potato and tomato plots. Rogue and bury infected plants immediately. Halt furrow flooding."
    },
    "Potato___healthy": {
        "crop": "Potato",
        "condition": "Healthy Foliage",
        "pathogen_type": "none",
        "is_healthy": True,
        "favorable_weather": "Optimal growing conditions",
        "targeted_guidance": "Continue scouting fields twice weekly, particularly following rainy periods. No intervention needed."
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "condition": "Bacterial Spot",
        "pathogen_type": "bacterial",
        "is_healthy": False,
        "favorable_weather": "Hot, wet rainy periods (25-30°C)",
        "targeted_guidance": "Avoid working in pepper rows when leaves are moist. Remove basal leaves showing watersoaked lesions. Rotate with corn or legumes."
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "condition": "Healthy Foliage",
        "pathogen_type": "none",
        "is_healthy": True,
        "favorable_weather": "Optimal growing conditions",
        "targeted_guidance": "Foliage is vigorous. Maintain consistent soil moisture to prevent blossom end rot. No intervention required."
    },
}


def parse_class_name(raw_name: str) -> Dict[str, Any]:
    """Parse raw PlantVillage folder string into normalized metadata."""
    if raw_name in CLASS_METADATA:
        meta = CLASS_METADATA[raw_name].copy()
        meta["raw_class"] = raw_name
        return meta

    # Generic parsing fallback for classes not in detailed lookup
    if "___" in raw_name:
        crop_part, condition_part = raw_name.split("___", 1)
    else:
        crop_part = "Unknown"
        condition_part = raw_name

    crop = crop_part.replace("_", " ").strip()
    condition = condition_part.replace("_", " ").strip()
    is_healthy = "healthy" in condition.lower()

    return {
        "raw_class": raw_name,
        "crop": crop,
        "condition": condition,
        "pathogen_type": "none" if is_healthy else "pathogen",
        "is_healthy": is_healthy,
        "favorable_weather": "Refer to local agronomist advisory",
        "targeted_guidance": "Maintain routine crop monitoring and sanitary cultural practices." if is_healthy else "Isolate affected plants and consult agricultural officer."
    }
