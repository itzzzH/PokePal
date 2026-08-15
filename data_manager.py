# data_manager.py
import json
import os

MASTER_DEX_DB = {}
LOCATION_ENCOUNTERS_DB = {}
MOVES_DB = {}
POKEMON_NAMES_LIST = []
EGG_GROUPS_DB = {}

def load_all_databases():
    global MASTER_DEX_DB, LOCATION_ENCOUNTERS_DB, MOVES_DB, POKEMON_NAMES_LIST, EGG_GROUPS_DB
    
    MASTER_DEX_DB.clear()
    LOCATION_ENCOUNTERS_DB.clear()
    MOVES_DB.clear()
    POKEMON_NAMES_LIST.clear()
    EGG_GROUPS_DB.clear()
    
    # Load Moves
    moves_paths = [os.path.join("data", "moves-data.json"), "moves-data.json", os.path.join("data", "moves.json"), "moves.json"]
    moves_file = next((p for p in moves_paths if os.path.exists(p)), None)
    if moves_file:
        try:
            with open(moves_file, "r", encoding="utf-8") as f:
                raw_moves = json.load(f)
                if isinstance(raw_moves, dict):
                    for m_key, m_entry in raw_moves.items():
                        if not isinstance(m_entry, dict): continue
                        MOVES_DB[m_key.lower().strip()] = m_entry
                        m_name_real = str(m_entry.get("name", "")).lower().strip()
                        if m_name_real:
                            MOVES_DB[m_name_real] = m_entry
                            MOVES_DB[m_name_real.replace(" ", "-")] = m_entry
                elif isinstance(raw_moves, list):
                    for m_entry in raw_moves:
                        if not isinstance(m_entry, dict): continue
                        m_name = str(m_entry.get("name", "")).lower().strip()
                        if m_name:
                            MOVES_DB[m_name] = m_entry
                            MOVES_DB[m_name.replace(" ", "-")] = m_entry
        except Exception as e:
            print(f"Error loading moves-data.json: {e}")

    # Load Monster / Pokedex
    monster_paths = [os.path.join("data", "monster.json"), "monster.json"]
    monster_file = next((p for p in monster_paths if os.path.exists(p)), None)
    if monster_file:
        try:
            with open(monster_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                entries = raw_data if isinstance(raw_data, list) else raw_data.get("monsters", raw_data.get("data", []))
                
                for entry in entries:
                    if not isinstance(entry, dict): continue
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
                        
                        if p_id: MASTER_DEX_DB[p_id] = entry
                        MASTER_DEX_DB[name.lower()] = entry
                        
                        if name_cap not in POKEMON_NAMES_LIST:
                            POKEMON_NAMES_LIST.append(name_cap)
                            if p_id:
                                POKEMON_NAMES_LIST.append(f"#{p_id} {name_cap}")
        except Exception as e:
            print(f"Error loading monster.json: {e}")

    # Load Locations
    loc_paths = [os.path.join("data", "locations-data.json"), "locations-data.json"]
    loc_file = next((p for p in loc_paths if os.path.exists(p)), None)
    if loc_file:
        try:
            with open(loc_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                horde_scale = content.get("hordeRateScale", 20)
                locations_list = content.get("locations", [])
                
                for zone in locations_list:
                    region_name = zone.get("region", "Unknown")
                    location_name = zone.get("name", "Unknown Area")
                    
                    for enc in zone.get("pokemon", []):
                        poke_name = str(enc.get("name", "")).strip().lower()
                        if not poke_name: continue
                            
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
                        
                        if poke_name not in LOCATION_ENCOUNTERS_DB:
                            LOCATION_ENCOUNTERS_DB[poke_name] = []
                        LOCATION_ENCOUNTERS_DB[poke_name].append(encounter_record)
        except Exception as e:
            print(f"Error loading locations-data.json: {e}")

    # Load Egg Groups
    egg_paths = [os.path.join("data", "egg-groups-data.json"), "egg-groups-data.json"]
    egg_file = next((p for p in egg_paths if os.path.exists(p)), None)
    if egg_file:
        try:
            with open(egg_file, "r", encoding="utf-8") as f:
                loaded_eggs = json.load(f)
                if isinstance(loaded_eggs, dict):
                    for k, group_data in loaded_eggs.items():
                        if not isinstance(group_data, dict): 
                            continue
                        group_name = str(group_data.get("name", "")).strip()
                        species_list = group_data.get("pokemon_species", [])
                        
                        for poke in species_list:
                            if not isinstance(poke, dict): 
                                continue
                            p_name = str(poke.get("name", "")).lower().strip()
                            if p_name:
                                if p_name not in EGG_GROUPS_DB:
                                    EGG_GROUPS_DB[p_name] = []
                                if group_name not in EGG_GROUPS_DB[p_name]:
                                    EGG_GROUPS_DB[p_name].append(group_name)
        except Exception as e:
            print(f"Error loading egg-groups-data.json: {e}")

def get_egg_groups(species_str):
    """Safely extracts and resolves egg groups regardless of formatting (#ID Name, multi-word names, etc.)."""
    if not species_str:
        return []
    
    clean_str = species_str.strip()
    if clean_str.startswith("#"):
        parts = clean_str.split(" ", 1)
        clean_str = parts[1] if len(parts) > 1 else clean_str[1:]
            
    clean_lower = clean_str.lower().strip()
    
    # Direct lookup
    if clean_lower in EGG_GROUPS_DB:
        return EGG_GROUPS_DB[clean_lower]
        
    # Hyphenated variation (e.g., "mr mime" -> "mr-mime")
    hyphenated = clean_lower.replace(" ", "-").replace(".", "")
    if hyphenated in EGG_GROUPS_DB:
        return EGG_GROUPS_DB[hyphenated]
        
    return []

def are_compatible(species1, gender1, species2, gender2):
    if gender1 == "Ditto" or gender2 == "Ditto":
        return True, "Compatible (Ditto)"
        
    if gender1 == gender2 and gender1 != "Unknown":
        return False, "Parents cannot be of the same gender!"

    groups1 = get_egg_groups(species1)
    groups2 = get_egg_groups(species2)

    if not groups1 or not groups2:
        return True, "Egg groups unknown (Assumed compatible)"

    undiscovered_variants = {"cannot-breed", "undiscovered", "no-eggs"}
    if any(str(g).lower() in undiscovered_variants for g in groups1) or any(str(g).lower() in undiscovered_variants for g in groups2):
        return False, "This species cannot breed (Undiscovered group)!"

    shared = set(str(g).lower() for g in groups1).intersection(set(str(g).lower() for g in groups2))
    if shared:
        return True, "Compatible (Shared group)"
        
    return False, "Parents do not share an Egg Group!"

class DataManager:
    def __init__(self):
        load_all_databases()
        self.master_dex = MASTER_DEX_DB
        self.location_encounters = LOCATION_ENCOUNTERS_DB
        self.moves = MOVES_DB
        self.pokemon_names = POKEMON_NAMES_LIST
        self.egg_groups = EGG_GROUPS_DB

    def are_compatible(self, species1, gender1, species2, gender2):
        return are_compatible(species1, gender1, species2, gender2)