# widgets/encounters.py
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPixmapCache
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGroupBox, QSizeGrip, QCompleter, QTextEdit
)
from core.base_overlay import BaseOverlay
from core.utils import format_rate
import data_manager

class LocationsWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Locations", main_app)
        self.selected_season = "All Seasons"
        self.selected_encounter_type = "All Encounters"
        self._sprite_cache = {}
        
        # Enforce a minimum size to prevent the UI from shrinking into the broken column-stacking state
        self.setMinimumSize(600, 400)
        
        # Pre-flatten encounters and pre-resolve Pokémon IDs for high-performance searching
        self._all_encounters = []
        for poke_key, encounters in data_manager.LOCATION_ENCOUNTERS_DB.items():
            dex_entry = data_manager.MASTER_DEX_DB.get(poke_key.lower())
            if not dex_entry:
                for k, v in data_manager.MASTER_DEX_DB.items():
                    if v.get('_clean_name', '').lower() == poke_key.lower():
                        dex_entry = v
                        break
            poke_id = 1
            if dex_entry:
                try:
                    poke_id = int(dex_entry.get("_clean_id", 1))
                except:
                    pass
            
            for enc in encounters:
                if isinstance(enc, dict):
                    self._all_encounters.append((poke_key, poke_id, enc))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1E1E24;
                border-radius: 10px;
                border: 1px solid #363644;
            }
        """)
        
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(8, 8, 8, 8)
        c_layout.setSpacing(6)
        
        # Header Row with Title Only
        header_row = QHBoxLayout()
        header_lbl = QLabel("🗺️ Location Finder")
        header_lbl.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        header_row.addWidget(header_lbl)
        header_row.addStretch()
        c_layout.addLayout(header_row)

        # Search Bar Row
        search_row = QHBoxLayout()
        search_row.setSpacing(4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Pokémon, Route, or Location...")
        
        # Build comprehensive completer list (Pokémon names + unique locations/regions)
        completion_items = set(data_manager.POKEMON_NAMES_LIST or [])
        for _, _, enc in self._all_encounters:
            loc = enc.get("location")
            reg = enc.get("region")
            if loc: completion_items.add(str(loc))
            if reg: completion_items.add(str(reg))

        if completion_items:
            completer = QCompleter(list(completion_items), self.search_input)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.search_input.setCompleter(completer)
            
        self.search_input.returnPressed.connect(self.perform_search)
        
        btn_search = QPushButton("Search")
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
        
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(btn_search)
        c_layout.addLayout(search_row)

        # Filters Box
        filters_box = QGroupBox("Filters")
        filters_box.setStyleSheet("""
            QGroupBox { color: #8F8FA8; font-size: 10px; font-weight: bold; border: 1px solid #282836; border-radius: 6px; margin-top: 4px; padding-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """)
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

        # Season Row
        season_row = QHBoxLayout()
        season_row.setContentsMargins(0, 0, 0, 0)
        season_row.setSpacing(2)
        season_lbl = QLabel("Season:")
        season_lbl.setStyleSheet("color: #A0A0B0; font-size: 10px; border: none;")
        season_row.addWidget(season_lbl)
        
        self.season_buttons = {}
        seasons = ["All Seasons", "Spring", "Summer", "Autumn", "Winter"]
        for s in seasons:
            btn = QPushButton(s)
            btn.setMinimumHeight(24)
            btn.setCheckable(True)
            btn.setStyleSheet(self.filter_btn_style)
            if s == self.selected_season: btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=s: self.set_season_filter(val))
            season_row.addWidget(btn)
            self.season_buttons[s] = btn
        f_layout.addLayout(season_row)

        # Type Row
        enc_row = QHBoxLayout()
        enc_row.setContentsMargins(0, 0, 0, 0)
        enc_row.setSpacing(2)
        enc_lbl = QLabel("Type:")
        enc_lbl.setStyleSheet("color: #A0A0B0; font-size: 10px; border: none;")
        enc_row.addWidget(enc_lbl)
        
        self.enc_buttons = {}
        enc_types = ["All Encounters", "Single", "Horde Only", "Lure Only"]
        for et in enc_types:
            btn = QPushButton(et)
            btn.setMinimumHeight(24)
            btn.setCheckable(True)
            btn.setStyleSheet(self.filter_btn_style)
            if et == self.selected_encounter_type: btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=et: self.set_encounter_filter(val))
            enc_row.addWidget(btn)
            self.enc_buttons[et] = btn
        f_layout.addLayout(enc_row)

        c_layout.addWidget(filters_box)

        # Results Area
        results_box = QGroupBox("Encounter Results")
        results_box.setStyleSheet("""
            QGroupBox { color: #8F8FA8; font-size: 10px; font-weight: bold; border: 1px solid #282836; border-radius: 6px; margin-top: 4px; padding-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """)
        r_layout = QVBoxLayout(results_box)
        r_layout.setContentsMargins(4, 4, 4, 4)
        
        self.results_text_area = QTextEdit()
        self.results_text_area.setReadOnly(True)
        self.results_text_area.setStyleSheet("background: #141418; border: none; color: #E2E2E8; font-size: 11px;")
        r_layout.addWidget(self.results_text_area)
        
        c_layout.addWidget(results_box, 1)
        layout.addWidget(container)

        if "locations_pos" in self.main_app.config:
            self.move(*self.main_app.config["locations_pos"])
        if "locations_size" in self.main_app.config:
            self.resize(*self.main_app.config["locations_size"])
        else:
            self.resize(540, 560)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        self.perform_search()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def set_season_filter(self, val):
        self.selected_season = val
        for s, btn in self.season_buttons.items():
            btn.setChecked(s == val)
        self.perform_search()

    def set_encounter_filter(self, val):
        self.selected_encounter_type = val
        for et, btn in self.enc_buttons.items():
            btn.setChecked(et == val)
        self.perform_search()

    def perform_search(self):
        query = self.search_input.text().strip().lower()
        if query.startswith("#"):
            query = query[1:]
        
        target = query
        if query.isdigit():
            entry = data_manager.MASTER_DEX_DB.get(str(int(query)))
            if entry:
                target = entry.get('_clean_name', '').lower()
        else:
            entry = data_manager.MASTER_DEX_DB.get(query)
            if entry:
                target = entry.get('_clean_name', '').lower()
            else:
                for k, v in data_manager.MASTER_DEX_DB.items():
                    if v.get('_clean_name', '').lower() == query:
                        target = query
                        break

        rows_data = []

        # Encounter-centric evaluation optimized via pre-flattened list
        for poke_key, poke_id, enc in self._all_encounters:
            region = str(enc.get("region", "Unknown"))
            sub_area = str(enc.get("location", "Unknown Area"))
            m_type = str(enc.get("type", "Grass"))

            # Check if query matches Pokémon name, region, location, or encounter type
            if target:
                match_target = (
                    target in poke_key.lower() or
                    target in region.lower() or
                    target in sub_area.lower() or
                    target in m_type.lower()
                )
                if not match_target:
                    continue

            # Season filter check
            season = str(enc.get("season", "Any"))
            if self.selected_season != "All Seasons":
                if season != "Any" and self.selected_season.lower() not in season.lower():
                    continue

            region_title = region.title()
            sub_area_title = sub_area.title()
            formatted_type = m_type.capitalize()
            
            min_lvl = enc.get("minLevel", "?")
            max_lvl = enc.get("maxLevel", "?")
            lvl_str = f"{min_lvl}" if min_lvl == max_lvl else f"{min_lvl}-{max_lvl}" if min_lvl != "?" else str(min_lvl)

            horde_scale = enc.get("hordeRateScale", 20)
            is_horde3 = enc.get("horde3", False)
            is_horde5 = enc.get("horde5", False)
            is_horde = is_horde3 or is_horde5 or "horde" in formatted_type.lower()
            is_sweet = "sweet scent" in formatted_type.lower()

            if is_horde3:
                formatted_type = "3x Horde"
            elif is_horde5:
                formatted_type = "5x Horde"
            elif "horde" in formatted_type.lower():
                formatted_type = "Horde"

            morning_rate = format_rate(enc.get("morning"), is_horde, is_sweet, horde_scale)
            day_rate = format_rate(enc.get("day"), is_horde, is_sweet, horde_scale)
            night_rate = format_rate(enc.get("night"), is_horde, is_sweet, horde_scale)

            # Apply encounter type filtering rules
            if self.selected_encounter_type == "Single" and (is_horde or "lure" in formatted_type.lower()):
                continue
            if self.selected_encounter_type == "Horde Only" and not is_horde:
                continue
            if self.selected_encounter_type == "Lure Only" and "lure" not in formatted_type.lower():
                continue

            # Cached sprite URL check
            if poke_id not in self._sprite_cache:
                sprite_url = ""
                for p in [
                    os.path.join("data", "sprites", f"{poke_id}.png"),
                    os.path.join("sprites", f"{poke_id}.png"),
                    f"{poke_id}.png"
                ]:
                    if os.path.exists(p):
                        abs_p = os.path.abspath(p)
                        sprite_url = f"file:///{abs_p.replace(os.sep, '/')}"
                        break
                self._sprite_cache[poke_id] = sprite_url
            else:
                sprite_url = self._sprite_cache[poke_id]

            rows_data.append({
                "pokemon": poke_key.capitalize(),
                "sprite_url": sprite_url,
                "type": formatted_type,
                "region": region_title,
                "location": sub_area_title,
                "level": lvl_str,
                "season": season,
                "morning": morning_rate,
                "day": day_rate,
                "night": night_rate
            })

        if rows_data:
            html_parts = [
                """
                <table width='100%' style='border-collapse: collapse;'>
                    <thead>
                        <tr style='color: #80A0FF; font-weight: bold; text-align: left;'>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; width: 44px; text-align: center;'></th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; white-space: nowrap;'>Pokémon</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; white-space: nowrap;'>Type</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50;'>Region / Location</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; text-align: center; white-space: nowrap;'>Lvl</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; text-align: center; white-space: nowrap;'>Season</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; text-align: center; white-space: nowrap;'>🌅</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; text-align: center; white-space: nowrap;'>☀️</th>
                            <th style='padding: 6px 4px; border-bottom: 2px solid #3E3E50; text-align: center; white-space: nowrap;'>🌙</th>
                        </tr>
                    </thead>
                    <tbody>
                """
            ]
            for idx, r in enumerate(rows_data[:150]):
                bg_color = "#1A1A22" if idx % 2 == 0 else "#14141A"
                m_color = "#FFAA00" if r['morning'] != "--" else "#666677"
                d_color = "#55FF55" if r['day'] != "--" else "#666677"
                n_color = "#8080FF" if r['night'] != "--" else "#666677"

                img_tag = f"<img src='{r['sprite_url']}' style='width: 36px; height: 36px; object-fit: contain;'>" if r['sprite_url'] else ""

                html_parts.append(f"""
                    <tr style='background-color: {bg_color}; border-bottom: 1px solid #282834;'>
                        <td style='padding: 4px; text-align: center; vertical-align: middle;'>{img_tag}</td>
                        <td style='padding: 6px 4px; font-weight: bold; color: #FFFFFF; vertical-align: middle; white-space: nowrap;'>{r['pokemon']}</td>
                        <td style='padding: 6px 4px; font-weight: bold; color: #90CDF4; vertical-align: middle; white-space: nowrap;'>{r['type']}</td>
                        <td style='padding: 6px 4px; color: #D0D0DC; vertical-align: middle;'>{r['region']} - {r['location']}</td>
                        <td style='padding: 6px 4px; text-align: center; color: #A0C0E0; vertical-align: middle; white-space: nowrap;'>{r['level']}</td>
                        <td style='padding: 6px 4px; text-align: center; color: #D2D2E0; vertical-align: middle; white-space: nowrap;'>{r['season']}</td>
                        <td style='padding: 6px 4px; text-align: center; color: {m_color}; font-weight: bold; vertical-align: middle; white-space: nowrap;'>{r['morning']}</td>
                        <td style='padding: 6px 4px; text-align: center; color: {d_color}; font-weight: bold; vertical-align: middle; white-space: nowrap;'>{r['day']}</td>
                        <td style='padding: 6px 4px; text-align: center; color: {n_color}; font-weight: bold; vertical-align: middle; white-space: nowrap;'>{r['night']}</td>
                    </tr>
                """)
            html_parts.append("</tbody></table>")
            html = "".join(html_parts)
        else:
            html = "<div style='color: #888899; padding: 10px; text-align: center;'>No encounters found matching your search and filter criteria.</div>"

        self.results_text_area.setHtml(html)