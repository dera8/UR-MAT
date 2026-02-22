import unreal
import random
import math

# Bounding box entro cui spawnare le camere
X_RANGE = (-8000, 8000)
Y_RANGE = (-8000, 8000)
Z_BASE = 200  # Altezza di base da terra
Z_JITTER = (0, 300)  # Variazione verticale casuale

def look_at_rotation(from_pos, to_pos):
    """Calcola una rotazione per guardare da from_pos verso to_pos."""
    direction = to_pos - from_pos
    dx, dy, dz = direction.x, direction.y, direction.z

    yaw = math.degrees(math.atan2(dy, dx))
    distance_xy = math.sqrt(dx ** 2 + dy ** 2)
    pitch = math.degrees(math.atan2(dz, distance_xy))

    return unreal.Rotator(pitch, yaw, 0)

def spawn_random_fusion_cameras(num_cameras=10):
    editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    fusion_camera_class = unreal.load_class(None, "/Script/UnrealCV.FusionCameraActor")

    for i in range(num_cameras):
        # Posizione casuale
        x = random.uniform(*X_RANGE)
        y = random.uniform(*Y_RANGE)
        z = Z_BASE + random.uniform(*Z_JITTER)

        position = unreal.Vector(x, y, z)

        # Guarda leggermente in basso
        target = unreal.Vector(x, y, 0)

        rotation = look_at_rotation(position, target)

        camera = editor_subsystem.spawn_actor_from_class(fusion_camera_class, position, rotation)
        camera.set_actor_label(f"FusionCamera_{i+1}")

    unreal.log(f"✅ {num_cameras} FusionCameraActor sparse spawned.")

# Esegui
spawn_random_fusion_cameras()
