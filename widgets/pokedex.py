# widgets/pokedex.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPixmapCache
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGroupBox, QSizeGrip, QProgressBar, QCompleter, QTextEdit, QWidget
)
from core.base_overlay import BaseOverlay
from core.utils import format_rate
import data_manager

class PokedexWidget(BaseOverlay):
    MODES = ["Front", "Back", "Shiny"]

    def __init__(self, main_app):
        super().__init__("Pokedex", main_app)
        self.current_id = 1
        self.sprite_mode = 0
        self.selected_season = "All Seasons"
        self.selected_encounter_type = "All Encounters"
        self.active_view = "locations"

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1E1E24;
                border-radius: 10px;
                border: 1px solid #363644;
            }
        """)
        
        self.c_layout = QVBoxLayout(self.container)
        self.c_layout.setContentsMargins(8, 8, 8, 8)
        self.c_layout.setSpacing(6)
        
        top_bar = QHBoxLayout()
        top_bar.setSpacing(4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Pokémon (Name or #ID)...")
        if data_manager.POKEMON_NAMES_LIST:
            completer = QCompleter(data_manager.POKEMON_NAMES_LIST, self.search_input)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.search_input.setCompleter(completer)
            
        self.search_input.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("Find")
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        btn_search.clicked.connect(self.perform_search)
        
        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(btn_search)
        self.c_layout.addLayout(top_bar)
        
        mid_info_layout = QHBoxLayout()
        mid_info_layout.setSpacing(10)
        
        sprite_box = QVBoxLayout()
        sprite_box.setSpacing(2)
        
        self.sprite_lbl = QLabel()
        self.sprite_lbl.setFixedSize(130, 130)
        self.sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_lbl.setStyleSheet("background: #141418; border: 1px solid #282832; border-radius: 6px;")
        self.sprite_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sprite_lbl.setToolTip("Click to toggle: Front -> Back -> Shiny")
        self.sprite_lbl.mousePressEvent = self.cycle_sprite_mode
        
        self.sprite_mode_lbl = QLabel("Front", self.sprite_lbl)
        self.sprite_mode_lbl.setGeometry(10, 102, 110, 20)
        self.sprite_mode_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_mode_lbl.setStyleSheet("""
            color: #80A0FF; 
            font-size: 10px; 
            font-weight: bold; 
            background: rgba(20, 20, 24, 210); 
            border-radius: 4px; 
            border: none;
        """)

        sprite_box.addWidget(self.sprite_lbl)
        mid_info_layout.addLayout(sprite_box)
        
        right_info_layout = QVBoxLayout()
        right_info_layout.setSpacing(3)
        
        self.name_lbl = QLabel("#1 Bulbasaur")
        self.name_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        
        self.type_lbl = QLabel("Grass / Poison")
        self.type_lbl.setStyleSheet("color: #90CDF4; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        
        self.ability_lbl = QLabel("Abilities: Overgrow")
        self.ability_lbl.setStyleSheet("color: #D2D2E0; font-size: 10px; border: none; background: transparent;")
        
        self.evo_lbl = QLabel("Evolution: Ivysaur")
        self.evo_lbl.setStyleSheet("color: #D2D2E0; font-size: 10px; border: none; background: transparent;")
        
        right_info_layout.addWidget(self.name_lbl)
        right_info_layout.addWidget(self.type_lbl)
        right_info_layout.addWidget(self.ability_lbl)
        right_info_layout.addWidget(self.evo_lbl)
        mid_info_layout.addLayout(right_info_layout)
        
        self.c_layout.addLayout(mid_info_layout)
        
        stats_box = QGroupBox("Base Stats")
        s_layout = QVBoxLayout(stats_box)
        s_layout.setContentsMargins(6, 6, 6, 6)
        s_layout.setSpacing(2)
        
        self.stat_bars = {}
        for stat_name in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]:
            row_l = QHBoxLayout()
            row_l.setSpacing(4)
            lbl = QLabel(stat_name)
            lbl.setFixedWidth(28)
            lbl.setStyleSheet("color: #A0A0B0; font-size: 10px; border: none; background: transparent;")
            pbar = QProgressBar()
            pbar.setRange(0, 255)
            pbar.setValue(50)
            pbar.setFormat("%v")
            row_l.addWidget(lbl)
            row_l.addWidget(pbar)
            s_layout.addLayout(row_l)
            self.stat_bars[stat_name.lower() if stat_name != "Atk" else "attack"] = pbar
            
        self.c_layout.addWidget(stats_box)
        
        filters_box = QGroupBox("Encounters & Info Options")
        f_layout = QVBoxLayout(filters_box)
        f_layout.setContentsMargins(6, 6, 6, 6)
        f_layout.setSpacing(4)

        self.filter_btn_style = """
            QPushButton {
                background-color: #252530;
                color: #C0C0D0;
                border: 1px solid #3E3E50;
                border-radius: 4px;
                padding: 3px 5px;
                font-size: 10px;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: #FFFFFF;
                font-weight: bold;
                border: 1px solid #60A5FA;
            }
            QPushButton:hover {
                background-color: #2D2D3B;
            }
        """
        
        view_row = QHBoxLayout()
        view_row.setSpacing(4)
        self.btn_view_loc = QPushButton("Locations")
        self.btn_view_loc.setCheckable(True)
        self.btn_view_loc.setChecked(True)
        self.btn_view_loc.setMinimumHeight(28)
        self.btn_view_loc.setStyleSheet(self.filter_btn_style)
        self.btn_view_loc.clicked.connect(lambda: self.switch_view("locations"))
        
        self.btn_view_mov = QPushButton("Moves / Learnset")
        self.btn_view_mov.setCheckable(True)
        self.btn_view_mov.setMinimumHeight(28)
        self.btn_view_mov.setStyleSheet(self.filter_btn_style)
        self.btn_view_mov.clicked.connect(lambda: self.switch_view("moves"))
        
        view_row.addWidget(self.btn_view_loc)
        view_row.addWidget(self.btn_view_mov)
        f_layout.addLayout(view_row)

        self.season_widget_container = QWidget()
        season_row = QHBoxLayout(self.season_widget_container)
        season_row.setContentsMargins(0, 0, 0, 0)
        season_row.setSpacing(2)
        season_lbl = QLabel("Season:")
        season_lbl.setStyleSheet("color: #A0A0B0; font-size: 10px;")
        season_row.addWidget(season_lbl)
        
        self.season_buttons = {}
        seasons = ["All Seasons", "Spring", "Summer", "Autumn", "Winter"]
        for s in seasons:
            btn = QPushButton(s)
            btn.setMinimumHeight(26)
            btn.setCheckable(True)
            btn.setStyleSheet(self.filter_btn_style)
            if s == self.selected_season: btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=s: self.set_season_filter(val))
            season_row.addWidget(btn)
            self.season_buttons[s] = btn
        f_layout.addWidget(self.season_widget_container)

        self.encounter_widget_container = QWidget()
        enc_row = QHBoxLayout(self.encounter_widget_container)
        enc_row.setContentsMargins(0, 0, 0, 0)
        enc_row.setSpacing(2)
        enc_lbl = QLabel("Type:")
        enc_lbl.setStyleSheet("color: #A0A0B0; font-size: 10px;")
        enc_row.addWidget(enc_lbl)
        
        self.enc_buttons = {}
        enc_types = ["All Encounters", "Normal / Grass", "Horde Only", "Lure Only"]
        for et in enc_types:
            btn = QPushButton(et)
            btn.setMinimumHeight(26)
            btn.setCheckable(True)
            btn.setStyleSheet(self.filter_btn_style)
            if et == self.selected_encounter_type: btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=et: self.set_encounter_filter(val))
            enc_row.addWidget(btn)
            self.enc_buttons[et] = btn
        f_layout.addWidget(self.encounter_widget_container)

        self.c_layout.addWidget(filters_box)
        
        loc_box = QGroupBox("Data Display")
        l_layout = QVBoxLayout(loc_box)
        l_layout.setContentsMargins(2, 2, 2, 2)
        
        self.location_text_area = QTextEdit()
        self.location_text_area.setReadOnly(True)
        self.location_text_area.setStyleSheet("background: #141418; border: none; color: #E2E2E8; font-size: 11px;")
        l_layout.addWidget(self.location_text_area)
        self.c_layout.addWidget(loc_box, 1)

        self.layout.addWidget(self.container)

        if "pokedex_pos" in self.main_app.config:
            x, y = self.main_app.config["pokedex_pos"]
            self.move(x, y)
        if "pokedex_size" in self.main_app.config:
            w, h = self.main_app.config["pokedex_size"]
            self.resize(w, h)
        else:
            self.resize(480, 720)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        self.load_pokemon_data(1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def switch_view(self, mode):
        self.active_view = mode
        self.btn_view_loc.setChecked(mode == "locations")
        self.btn_view_mov.setChecked(mode == "moves")
        is_loc = (mode == "locations")
        self.season_widget_container.setVisible(is_loc)
        self.encounter_widget_container.setVisible(is_loc)
        self.load_pokemon_data(self.current_id)

    def set_season_filter(self, val):
        self.selected_season = val
        for s, btn in self.season_buttons.items():
            btn.setChecked(s == val)
        self.load_pokemon_data(self.current_id)

    def set_encounter_filter(self, val):
        self.selected_encounter_type = val
        for et, btn in self.enc_buttons.items():
            btn.setChecked(et == val)
        self.load_pokemon_data(self.current_id)

    def cycle_sprite_mode(self, event=None):
        self.sprite_mode = (self.sprite_mode + 1) % 3
        self.sprite_mode_lbl.setText(self.MODES[self.sprite_mode])
        self.load_sprite()

    def perform_search(self):
        txt = self.search_input.text().strip()
        if not txt: return
        if txt.startswith("#"): txt = txt[1:]
        parts = txt.split(" ")
        query_val = parts[0].lower()
        
        found_id = None
        if query_val.isdigit():
            found_id = int(query_val)
        else:
            entry = data_manager.MASTER_DEX_DB.get(query_val)
            if entry:
                found_id = int(entry.get("_clean_id", 1))
        if found_id:
            self.load_pokemon_data(found_id)

    def load_sprite(self):
        """Loads sprite pixmap (120x120) with QPixmapCache caching."""
        mode_str = self.MODES[self.sprite_mode].lower()
        cid = self.current_id
        cache_key = f"pokedex_sprite_{mode_str}_{cid}"

        pix = QPixmapCache.find(cache_key)

        if pix is None:
            if mode_str == "front":
                paths = [os.path.join("data", "sprites", f"{cid}.png"), os.path.join("sprites", f"{cid}.png"), f"{cid}.png"]
            elif mode_str == "back":
                paths = [os.path.join("data", "sprites", "back", f"{cid}.png"), os.path.join("sprites", f"{cid}_back.png"), f"{cid}_back.png"]
            else:
                paths = [os.path.join("data", "sprites", "shiny", f"{cid}.png"), os.path.join("sprites", f"{cid}_shiny.png"), f"{cid}_shiny.png"]

            for p in paths:
                if os.path.exists(p):
                    loaded_pix = QPixmap(p)
                    if not loaded_pix.isNull():
                        pix = loaded_pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        QPixmapCache.insert(cache_key, pix)
                    break

        if pix and not pix.isNull():
            self.sprite_lbl.setPixmap(pix)
            self.sprite_lbl.setText("")
        else:
            self.sprite_lbl.setPixmap(QPixmap())
            self.sprite_lbl.setText(f"No {self.MODES[self.sprite_mode]}")

    def update_stats_bars(self, stats):
        if isinstance(stats, list) and len(stats) >= 6:
            stat_order = ["hp", "attack", "def", "spa", "spd", "spe"]
            for idx, stat_key in enumerate(stat_order):
                if stat_key in self.stat_bars:
                    self.stat_bars[stat_key].setValue(int(stats[idx]))
            return

        key_map = {
            "hp": ["hp", "base_hp"], 
            "attack": ["attack", "atk", "base_attack"], 
            "def": ["defense", "def", "base_defense"],
            "spa": ["special-attack", "sp_attack", "sp. atk", "spa"], 
            "spd": ["special-defense", "sp_defense", "sp. def", "spd"], 
            "spe": ["speed", "spe", "base_speed"]
        }
        
        for stat_key, bar in self.stat_bars.items():
            possible_keys = key_map.get(stat_key, [stat_key])
            val = 50
            
            if isinstance(stats, dict):
                for k in possible_keys:
                    if k in stats:
                        val = stats[k]
                        break
            bar.setValue(int(val))

    def load_pokemon_data(self, poke_id):
        self.current_id = int(poke_id)
        entry = data_manager.MASTER_DEX_DB.get(str(self.current_id))
        if not entry:
            self.name_lbl.setText(f"#{self.current_id} Unknown")
            self.type_lbl.setText("-")
            self.ability_lbl.setText("Abilities: -")
            self.evo_lbl.setText("Evolution: -")
            self.location_text_area.setHtml("<div style='color: #888899; padding: 10px;'>No entry found.</div>")
            return

        name_str = f"#{self.current_id} {entry.get('_clean_name', 'Unknown')}"
        types = entry.get("types", [])
        types_str = " / ".join([str(t).capitalize() for t in types]) if types else "-"
        
        abilities = entry.get("abilities", [])
        unique_abilities = []
        for ab in abilities:
            ab_name = ab.get("name") if isinstance(ab, dict) else str(ab)
            if ab_name and ab_name not in unique_abilities:
                unique_abilities.append(ab_name)
        abilities_str = ", ".join(unique_abilities) if unique_abilities else "-"

        stats = entry.get("stats", {})
        self.update_stats_bars(stats)

        evolutions = entry.get("evolutions", [])
        unique_evos = []
        for evo in evolutions:
            evo_name = evo.get("name") if isinstance(evo, dict) else str(evo)
            if evo_name and evo_name not in unique_evos:
                unique_evos.append(evo_name)
        evo_str = " ➔ ".join(unique_evos) if unique_evos else "None"

        self.load_sprite()
        
        if self.active_view == "moves":
            moves = entry.get("moves", entry.get("learnset", []))
            if moves:
                moves_html = """
                <table width='100%' style='border-collapse: collapse;'>
                    <thead>
                        <tr style='color: #80A0FF; font-weight: bold; text-align: left;'>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>Lvl</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Move Name</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Type</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Cat</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>Pwr</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>Acc</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>PP</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for idx, m in enumerate(moves):
                    bg_color = "#1A1A22" if idx % 2 == 0 else "#14141A"
                    if isinstance(m, dict):
                        m_lvl = m.get("level", m.get("lvl", "-"))
                        m_raw_name = m.get("name", m.get("move", "Unknown"))
                    else:
                        m_lvl = "-"
                        m_raw_name = str(m)
                    
                    lookup_key = str(m_raw_name).lower().strip()
                    lookup_key_hyphen = lookup_key.replace(" ", "-")
                    m_db_info = data_manager.MOVES_DB.get(lookup_key) or data_manager.MOVES_DB.get(lookup_key_hyphen) or {}
                    
                    m_name = m_db_info.get("name", m_raw_name)
                    if isinstance(m_name, str): m_name = m_name.title()
                        
                    m_type = str(m_db_info.get("type", m.get("type", "-"))).capitalize()
                    raw_cat = m_db_info.get("damage_class", m_db_info.get("category", m.get("category", "-")))
                    m_cat = str(raw_cat).capitalize()
                    
                    m_pwr = m_db_info.get("power", m.get("power", "-"))
                    if m_pwr is None or m_pwr == "": m_pwr = "-"
                        
                    m_acc = m_db_info.get("accuracy", m.get("accuracy", "-"))
                    if isinstance(m_acc, float) and m_acc <= 1.0: m_acc = f"{int(m_acc * 100)}%"
                    elif isinstance(m_acc, (int, float)) and m_acc > 1.0: m_acc = f"{int(m_acc)}%"
                    elif m_acc is None or m_acc == "": m_acc = "-"
                        
                    m_pp = m_db_info.get("pp", m.get("pp", "-"))
                    if m_pp is None or m_pp == "": m_pp = "-"

                    moves_html += f"""
                        <tr style='background-color: {bg_color}; border-bottom: 1px solid #282834;'>
                            <td style='padding: 4px; text-align: center; color: #A0C0E0;'>{m_lvl}</td>
                            <td style='padding: 4px; font-weight: bold; color: #FFFFFF;'>{m_name}</td>
                            <td style='padding: 4px; color: #90CDF4;'>{m_type}</td>
                            <td style='padding: 4px; color: #D0D0DC;'>{m_cat}</td>
                            <td style='padding: 4px; text-align: center; color: #FFAA00;'>{m_pwr}</td>
                            <td style='padding: 4px; text-align: center; color: #55FF55;'>{m_acc}</td>
                            <td style='padding: 4px; text-align: center; color: #8080FF;'>{m_pp}</td>
                        </tr>
                    """
                moves_html += "</tbody></table>"
            else:
                moves_html = "<div style='color: #888899; padding: 10px; text-align: center;'>No move data available for this Pokémon.</div>"
            self.location_text_area.setHtml(moves_html)
        else:
            poke_key = entry.get('_clean_name', '').lower()
            encounters = data_manager.LOCATION_ENCOUNTERS_DB.get(poke_key, [])

            rows_data = []
            for enc in encounters:
                if not isinstance(enc, dict): continue
                season = str(enc.get("season", "Any"))
                if self.selected_season != "All Seasons":
                    if season != "Any" and self.selected_season.lower() not in season.lower():
                        continue

                region = str(enc.get("region", "Unknown")).title()
                sub_area = str(enc.get("location", "Unknown Area")).title()
                m_type = str(enc.get("type", "Grass")).capitalize()
                
                min_lvl = enc.get("minLevel", "?")
                max_lvl = enc.get("maxLevel", "?")
                lvl_str = f"{min_lvl}" if min_lvl == max_lvl else f"{min_lvl}-{max_lvl}" if min_lvl != "?" else str(min_lvl)

                horde_scale = enc.get("hordeRateScale", 20)
                is_horde = enc.get("horde3", False) or enc.get("horde5", False) or "horde" in m_type.lower()
                is_sweet = "sweet scent" in m_type.lower()

                morning_rate = format_rate(enc.get("morning"), is_horde, is_sweet, horde_scale)
                day_rate = format_rate(enc.get("day"), is_horde, is_sweet, horde_scale)
                night_rate = format_rate(enc.get("night"), is_horde, is_sweet, horde_scale)

                if self.selected_encounter_type == "Horde Only" and not is_horde: continue
                if self.selected_encounter_type == "Lure Only" and "lure" not in m_type.lower(): continue

                rows_data.append({"type": m_type, "region": region, "location": sub_area, "level": lvl_str, "morning": morning_rate, "day": day_rate, "night": night_rate})

            if rows_data:
                location_display_html = """
                <table width='100%' style='border-collapse: collapse;'>
                    <thead>
                        <tr style='color: #80A0FF; font-weight: bold; text-align: left;'>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Type</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Region</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50;'>Location</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>Lvl</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>🌅</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>☀️</th>
                            <th style='padding: 4px; border-bottom: 2px solid #3E3E50; text-align: center;'>🌙</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                for idx, r in enumerate(rows_data):
                    bg_color = "#1A1A22" if idx % 2 == 0 else "#14141A"
                    m_color = "#FFAA00" if r['morning'] != "--" else "#666677"
                    d_color = "#55FF55" if r['day'] != "--" else "#666677"
                    n_color = "#8080FF" if r['night'] != "--" else "#666677"

                    location_display_html += f"""
                        <tr style='background-color: {bg_color}; border-bottom: 1px solid #282834;'>
                            <td style='padding: 4px; font-weight: bold; color: #90CDF4;'>{r['type']}</td>
                            <td style='padding: 4px; color: #D0D0DC;'>{r['region']}</td>
                            <td style='padding: 4px; font-weight: bold; color: #FFFFFF;'>{r['location']}</td>
                            <td style='padding: 4px; text-align: center; color: #A0C0E0;'>{r['level']}</td>
                            <td style='padding: 4px; text-align: center; color: {m_color}; font-weight: bold;'>{r['morning']}</td>
                            <td style='padding: 4px; text-align: center; color: {d_color}; font-weight: bold;'>{r['day']}</td>
                            <td style='padding: 4px; text-align: center; color: {n_color}; font-weight: bold;'>{r['night']}</td>
                        </tr>
                    """
                location_display_html += "</tbody></table>"
            else:
                location_display_html = "<div style='color: #888899; padding: 10px; text-align: center;'>No locations found matching filter criteria.</div>"

            self.location_text_area.setHtml(location_display_html)

        self.name_lbl.setText(name_str)
        self.type_lbl.setText(types_str)
        self.ability_lbl.setText(f"Abilities: {abilities_str}")
        self.evo_lbl.setText(f"Evolution: {evo_str}")