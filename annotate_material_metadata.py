import json

# 📚 Library of materials and associated physical properties
material_properties = {
    "Limestone": {"permittivity": 5.6, "attenuation": 0.006, "reflectance": 0.75},
    "Slate": {"permittivity": 6.1, "attenuation": 0.007, "reflectance": 0.65},
    "Glass": {"permittivity": 4.82, "attenuation": 0.005, "reflectance": 0.85},
    "Steel": {"permittivity": 1.0, "attenuation": 0.001, "reflectance": 0.95},
    "Brick": {"permittivity": 3.75, "attenuation": 0.008, "reflectance": 0.60},
    "Cobblestone": {"permittivity": 4.5, "attenuation": 0.007, "reflectance": 0.58},
    "Plaster": {"permittivity": 2.8, "attenuation": 0.005, "reflectance": 0.60},
    "Concrete": {"permittivity": 5.0, "attenuation": 0.008, "reflectance": 0.70},
    "Gravel": {"permittivity": 4.2, "attenuation": 0.007, "reflectance": 0.55},
    "Tiles": {"permittivity": 3.5, "attenuation": 0.006, "reflectance": 0.62},
    "Wood": {"permittivity": 2.2, "attenuation": 0.004, "reflectance": 0.50},
    "Asphalt": {"permittivity": 4.5, "attenuation": 0.01, "reflectance": 0.35},
    "Plastic": {"permittivity": 2.8, "attenuation": 0.006, "reflectance": 0.50},
    "Unknown": {"permittivity": 1.0, "attenuation": 0.01, "reflectance": 0.5}
}

# 🔍 Heuristic mapping from Unreal material keywords to physical material types
material_mapping = {
    "limestone": "Limestone",
    "slate": "Slate",
    "glass": "Glass",
    "steel": "Steel",
    "brick": "Brick",
    "cobblestone": "Cobblestone",
    "plaster": "Plaster",
    "concrete": "Concrete",
    "gravel": "Gravel",
    "tiles": "Tiles",
    "wood": "Wood",
    "asphalt": "Asphalt",
    "plastic": "Plastic"
}

def classify_material(material_path):
    for keyword, material_type in material_mapping.items():
        if keyword in material_path.lower():
            return material_type
    return "Unknown"

# 📂 Load materials by object and mesh section
input_path = "C:/.../scene_materials_name.json"
with open(input_path, "r") as f:
    scene_materials = json.load(f)

# 🧱 Generate final dictionary with material type and physical properties
scene_metadata = {}

for obj_name, section_dict in scene_materials.items():
    object_metadata = {}

    for section, material_path in section_dict.items():
        material_type = classify_material(material_path)
        properties = material_properties.get(material_type, material_properties["Unknown"])

        object_metadata[section] = {
            "material_path": material_path,
            "material_type": material_type,
            "physical_properties": properties
        }

    scene_metadata[obj_name] = object_metadata

# 💾 Save JSON with annotated metadata
output_path = "C:/.../scene_physical_metadata_name.json"
with open(output_path, "w") as f:
    json.dump(scene_metadata, f, indent=4)

print(f"✅ Physical metadata saved to {output_path}")
