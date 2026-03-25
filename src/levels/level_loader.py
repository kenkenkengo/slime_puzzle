"""Level data loading from JSON files."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SlimeStart:
    x: float
    y: float
    radius: float = 40.0
    num_particles: int = 12


@dataclass(frozen=True)
class TerrainData:
    vertices: tuple[tuple[float, float], ...]
    friction: float = 0.7


@dataclass(frozen=True)
class HazardData:
    rect: tuple[float, float, float, float]
    hazard_type: str = "spikes"


@dataclass(frozen=True)
class GoalData:
    rect: tuple[float, float, float, float]


@dataclass(frozen=True)
class LevelData:
    name: str
    slime_start: SlimeStart
    terrain: tuple[TerrainData, ...]
    goal: GoalData
    hazards: tuple[HazardData, ...] = ()
    par_time: float = 60.0


LEVEL_DIR = Path(__file__).parent / "level_data"


def load_level(level_id: int) -> LevelData:
    """Load a level from its JSON file."""
    path = LEVEL_DIR / f"level_{level_id:02d}.json"
    with open(path) as f:
        data = json.load(f)

    slime = data["slime_start"]
    slime_start = SlimeStart(
        x=slime["x"],
        y=slime["y"],
        radius=slime.get("radius", 40.0),
        num_particles=slime.get("num_particles", 12),
    )

    terrain_list = []
    for t in data.get("terrain", []):
        vertices = tuple(tuple(v) for v in t["vertices"])
        terrain_list.append(TerrainData(vertices=vertices, friction=t.get("friction", 0.7)))

    hazards_list = []
    for h in data.get("hazards", []):
        hazards_list.append(HazardData(rect=tuple(h["rect"]), hazard_type=h.get("type", "spikes")))

    goal = data["goal"]
    goal_data = GoalData(rect=tuple(goal["rect"]))

    return LevelData(
        name=data["name"],
        slime_start=slime_start,
        terrain=tuple(terrain_list),
        goal=goal_data,
        hazards=tuple(hazards_list),
        par_time=data.get("par_time", 60.0),
    )


def get_level_count() -> int:
    """Count available level files."""
    if not LEVEL_DIR.exists():
        return 0
    return len(list(LEVEL_DIR.glob("level_*.json")))
