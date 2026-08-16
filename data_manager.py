import json
import os
from pathlib import Path

MASTER_DEX_DB = {}
LOCATION_ENCOUNTERS_DB = {}
MOVES_DB = {}
POKEMON_NAMES_LIST = []
EGG_GROUPS_DB = {}

def _find_data_file(filename: str):
    """Finds the path for a target JSON file in ./data/ or current directory."""
    candidates = [Path("data") / filename, Path(filename)]
    for path in candidates:
        if path.exists():
            return path
    return None

def load_all_databases():
    global MASTER_DEX_DB, LOCATION_ENCOUNTERS_DB, MOVES_DB, POKEMON_NAMES_LIST, EGG_GROUPS_DB
    
    MASTER_DEX_DB.clear()
    LOCATION_ENCOUNTERS_DB.clear()
    MOVES_DB.clear()
    POKEMON_NAMES_LIST.clear()
    EGG_GROUPS_DB.clear()
    
    # Load Moves
    moves_file = _find_data_file("moves-data.json") or _find_data_file("moves.json")
    if moves_file:
        try:
            with open(moves_file, "r", encoding="utf-8") as f:
                raw_moves = json.load(f)
                entries = raw_moves.values() if isinstance(raw_moves, dict) else raw_moves
                for m_entry in entries:
                    if not isinstance(m_entry, dict):
                        continue
                    m_name = str(m_entry.get("name", "")).lower().strip()
                    if m_name:
                        MOVES_DB[m_name] = m_entry
                        MOVES_DB[m_name.replace(" ", "-")] = m_entry
        except Exception as e:
            print(f"Error loading moves database: {e}")

    # Load Monster / Pokedex
    monster_file = _find_data_file("monster.json")
    if monster_file:
        try:
            with open(monster_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                entries = raw_data if isinstance(raw_data, list) else raw_data.get("monsters", raw_data.get("data", []))
                
                for entry in entries:
                    if not isinstance(entry, dict): 
                        continue
                    p_id = str(entry.get("id", ""))
                    raw_name = entry.get("name", "")
                    
                    if isinstance(raw_name, dict):
                        name = str(raw_name.get("english") or raw_name.get("en") or next(iter(raw_name.values()), "")).strip()
                    else:
                        name = str(raw_name).strip()
                        
                    if name:
                        name_cap = name.capitalize()
                        entry["_clean_name"] = name_cap
                        entry["_clean_id"] = p_id
                        
                        if p_id: 
                            MASTER_DEX_DB[p_id] = entry
                        MASTER_DEX_DB[name.lower()] = entry
                        
                        if name_cap not in POKEMON_NAMES_LIST:
                            POKEMON_NAMES_LIST.append(name_cap)
                            if p_id:
                                POKEMON_NAMES_LIST.append(f"#{p_id} {name_cap}")
        except Exception as e:
            print(f"Error loading monster database: {e}")

    # Load Locations
    loc_file = _find_data_file("locations-data.json")
    if loc_file:
        try:
            with open(loc_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                horde_scale = content.get("hordeRateScale", 20)
                
                for zone in content.get("locations", []):
                    region_name = zone.get("region", "Unknown")
                    location_name = zone.get("name", "Unknown Area")
                    
                    for enc in zone.get("pokemon", []):
                        poke_name = str(enc.get("name", "")).strip().lower()
                        if not poke_name: 
                            continue
                            
                        encounter_record = {
                            "region": region_name,
                            "location": location_name,
                            "season": enc.get("season", "Any"),
                            "type": enc.get("encounter", "Grass"),
                            "minLevel": enc.get("minLevel", "?"),
                            "maxLevel": enc.get("maxLevel", "?"),
                            "morning": enc.get("morning", "--"),
                            "day": enc.get("day", "--"),
                            "night": enc.get("night", "--"),
                            "horde3": enc.get("horde3", False),
                            "horde5": enc.get("horde5", False),
                            "hordeRateScale": horde_scale
                        }
                        LOCATION_ENCOUNTERS_DB.setdefault(poke_name, []).append(encounter_record)
        except Exception as e:
            print(f"Error loading locations database: {e}")

    # Load Egg Groups
    egg_file = _find_data_file("egg-groups-data.json")
    if egg_file:
        try:
            with open(egg_file, "r", encoding="utf-8") as f:
                loaded_eggs = json.load(f)
                if isinstance(loaded_eggs, dict):
                    for group_data in loaded_eggs.values():
                        if not isinstance(group_data, dict): 
                            continue
                        group_name = str(group_data.get("name", "")).strip()
                        for poke in group_data.get("pokemon_species", []):
                            if isinstance(poke, dict):
                                p_name = str(poke.get("name", "")).lower().strip()
                                if p_name:
                                    groups = EGG_GROUPS_DB.setdefault(p_name, [])
                                    if group_name not in groups:
                                        groups.append(group_name)
        except Exception as e:
            print(f"Error loading egg groups database: {e}")


def get_egg_groups(species_str: str) -> list:
    """Safely extracts and resolves egg groups regardless of formatting (#ID Name, multi-word, etc.)."""
    if not species_str:
        return []
    
    clean_str = species_str.strip()
    if clean_str.startswith("#"):
        parts = clean_str.split(" ", 1)
        clean_str = parts[1] if len(parts) > 1 else clean_str[1:]
            
    clean_lower = clean_str.lower().strip()
    
    if clean_lower in EGG_GROUPS_DB:
        return EGG_GROUPS_DB[clean_lower]
        
    hyphenated = clean_lower.replace(" ", "-").replace(".", "")
    return EGG_GROUPS_DB.get(hyphenated, [])


def are_compatible(species1: str, gender1: str, species2: str, gender2: str) -> tuple[bool, str]:
    if gender1 == "Ditto" or gender2 == "Ditto":
        return True, "Compatible (Ditto)"
        
    if gender1 == gender2 and gender1 != "Unknown":
        return False, "Parents cannot be of the same gender!"

    groups1 = get_egg_groups(species1)
    groups2 = get_egg_groups(species2)

    if not groups1 or not groups2:
        return True, "Egg groups unknown (Assumed compatible)"

    undiscovered = {"cannot-breed", "undiscovered", "no-eggs"}
    if any(str(g).lower() in undiscovered for g in groups1 + groups2):
        return False, "This species cannot breed (Undiscovered group)!"

    shared = set(g.lower() for g in groups1).intersection(set(g.lower() for g in groups2))
    if shared:
        return True, "Compatible (Shared group)"
        
    return False, "Parents do not share an Egg Group!"