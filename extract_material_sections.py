
import unreal
import json

def get_materials_with_sections():
    """Retrieve materials per object, using StaticMeshActor IDs from Unreal Engine."""

    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = editor_actor_subsystem.get_all_level_actors()

    material_data = {}

    for actor in actors:
        # Use Unreal Engine's internal name (matches UnrealCV format)
        object_label = actor.get_name()  # This should return "StaticMeshActor_XXX"

        if isinstance(actor, unreal.StaticMeshActor):
            mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if mesh_component:
                materials = {}
                for i in range(mesh_component.get_num_materials()):
                    material_name = mesh_component.get_material(i)
                    section_label = f"Section_{i}"
                    materials[section_label] = material_name.get_path_name() if material_name else "None"

                material_data[object_label] = materials  # Store section-wise materials

    return material_data

# Save extracted materials per section
scene_materials = get_materials_with_sections()
save_path = "C:/Users/Debora/Desktop/scene_materials_trastevere.json"
with open(save_path, "w") as file:
    json.dump(scene_materials, file, indent=4)

print(f"✅ Scene materials (per section) saved to {save_path}!")
