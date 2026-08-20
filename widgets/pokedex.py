# widgets/pokedex.py
import os
import math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPixmapCache, QGuiApplication
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGroupBox, QSizeGrip, QProgressBar, QCompleter, QTextEdit,
    QWidget, QGridLayout, QSpinBox, QScrollArea, QSizePolicy
)
from core.base_overlay import BaseOverlay
import data_manager
from globals import NATURES_LIST

class PokedexWidget(BaseOverlay):
    MODES = ["Front", "Back", "Shiny"]

    @staticmethod
    def get_nature_modifiers(nature_name):
        """
        Derives stat buffs and nerfs dynamically using the standard 
        Pokémon nature order stored in NATURES_LIST from globals.py.
        """
        if nature_name not in NATURES_LIST:
            return {"up": None, "down": None}
        
        idx = NATURES_LIST.index(nature_name)
        
        if idx % 6 == 0:
            return {"up": None, "down": None}
        
        stats_order = ["Attack", "Defense", "Speed", "Special Attack", "Special Defense"]
        
        up_idx = idx // 5
        up_stat = stats_order[up_idx]
        
        local_idx = idx % 5
        rem_idx = local_idx - 1 if local_idx > up_idx else local_idx
        remaining_stats = [s for j, s in enumerate(stats_order) if j != up_idx]
        down_stat = remaining_stats[rem_idx]
        
        return {"up": up_stat, "down": down_stat}

    def __init__(self, main_app):
        super().__init__("Pokedex", main_app)
        self.current_id = 1
        self.sprite_mode = 0
        self.active_view = "calculator"

        # Minimum size restriction for calculator view to prevent breaking UI
        self.setMinimumSize(420, 720)

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
        stats_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
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
        
        filters_box = QGroupBox("View Options")
        filters_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
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
        
        self.btn_view_calc = QPushButton("Stat Calculator")
        self.btn_view_calc.setCheckable(True)
        self.btn_view_calc.setChecked(True)
        self.btn_view_calc.setMinimumHeight(28)
        self.btn_view_calc.setStyleSheet(self.filter_btn_style)
        self.btn_view_calc.clicked.connect(lambda: self.switch_view("calculator"))

        self.btn_view_mov = QPushButton("Moves / Learnset")
        self.btn_view_mov.setCheckable(True)
        self.btn_view_mov.setChecked(False)
        self.btn_view_mov.setMinimumHeight(28)
        self.btn_view_mov.setStyleSheet(self.filter_btn_style)
        self.btn_view_mov.clicked.connect(lambda: self.switch_view("moves"))
        
        view_row.addWidget(self.btn_view_calc)
        view_row.addWidget(self.btn_view_mov)
        f_layout.addLayout(view_row)

        self.c_layout.addWidget(filters_box)
        
        # Scroll area wrapper for views
        self.display_scroll = QScrollArea()
        self.display_scroll.setWidgetResizable(True)
        self.display_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.display_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.display_container = QWidget()
        self.display_layout = QVBoxLayout(self.display_container)
        self.display_layout.setContentsMargins(0, 0, 0, 0)
        self.display_layout.setSpacing(0)

        # Calculator View Widget
        self.calc_widget = QWidget()
        c_outer_layout = QVBoxLayout(self.calc_widget)
        c_outer_layout.setContentsMargins(0, 0, 0, 0)
        c_outer_layout.setSpacing(4)

        settings_box = QGroupBox("Configuration")
        settings_box.setStyleSheet(self._box_style())
        s_config_layout = QGridLayout(settings_box)
        s_config_layout.setContentsMargins(8, 6, 8, 6)
        s_config_layout.setHorizontalSpacing(10)
        s_config_layout.setVerticalSpacing(4)

        lbl_lvl = QLabel("Level:")
        lbl_lvl.setStyleSheet("color: #A0A0B2; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        s_config_layout.addWidget(lbl_lvl, 0, 0)
        
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(50)
        self.level_spin.setStyleSheet(self._input_style())
        self.level_spin.valueChanged.connect(self.calculate_stats)
        s_config_layout.addWidget(self.level_spin, 0, 1)

        lbl_nat = QLabel("Nature:")
        lbl_nat.setStyleSheet("color: #A0A0B2; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        s_config_layout.addWidget(lbl_nat, 0, 2)
        
        self.nature_input = QLineEdit()
        self.nature_input.setText("Hardy")
        self.nature_input.setPlaceholderText("Nature name")
        self.nature_input.setStyleSheet(self._input_style())
        
        if NATURES_LIST:
            nature_completer = QCompleter(NATURES_LIST, self.nature_input)
            nature_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            nature_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.nature_input.setCompleter(nature_completer)
            
        self.nature_input.textChanged.connect(self.calculate_stats)
        s_config_layout.addWidget(self.nature_input, 0, 3)
        c_outer_layout.addWidget(settings_box)

        stats_calc_box = QGroupBox("Stat Breakdown & Builder")
        stats_calc_box.setStyleSheet(self._box_style())
        st_layout = QVBoxLayout(stats_calc_box)
        st_layout.setContentsMargins(6, 6, 6, 6)
        st_layout.setSpacing(4)

        self.stat_rows = {}
        stat_names = [
            ("hp", "HP"), 
            ("attack", "Attack"), 
            ("defense", "Defense"), 
            ("sp_atk", "Sp. Atk"), 
            ("sp_def", "Sp. Def"), 
            ("speed", "Speed")
        ]

        for key, label in stat_names:
            row_frame = QFrame()
            row_frame.setStyleSheet("""
                QFrame {
                    background-color: #17171D;
                    border: 1px solid #282835;
                    border-radius: 5px;
                    padding: 2px;
                }
            """)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(6, 2, 6, 2)
            row_layout.setSpacing(4)

            lbl_name = QLabel(label)
            lbl_name.setFixedWidth(52)
            lbl_name.setStyleSheet("color: #90CDF4; font-size: 10px; font-weight: bold; border: none; background: transparent;")
            row_layout.addWidget(lbl_name)

            lbl_b = QLabel("Base:")
            lbl_b.setStyleSheet("color: #8F8FA8; font-size: 9px; border: none; background: transparent;")
            row_layout.addWidget(lbl_b)
            
            base_spin = QSpinBox()
            base_spin.setRange(1, 255)
            base_spin.setValue(45)
            base_spin.setFixedWidth(40); base_spin.setFixedHeight(20)
            base_spin.setStyleSheet(self._input_style())
            base_spin.valueChanged.connect(self.calculate_stats)
            row_layout.addWidget(base_spin)

            lbl_i = QLabel("IV:")
            lbl_i.setStyleSheet("color: #8F8FA8; font-size: 9px; border: none; background: transparent;")
            row_layout.addWidget(lbl_i)
            
            iv_spin = QSpinBox()
            iv_spin.setRange(0, 31)
            iv_spin.setValue(31)
            iv_spin.setFixedWidth(36); iv_spin.setFixedHeight(20)
            iv_spin.setStyleSheet(self._input_style())
            iv_spin.valueChanged.connect(self.calculate_stats)
            row_layout.addWidget(iv_spin)

            lbl_e = QLabel("EV:")
            lbl_e.setStyleSheet("color: #8F8FA8; font-size: 9px; border: none; background: transparent;")
            row_layout.addWidget(lbl_e)
            
            ev_spin = QSpinBox()
            ev_spin.setRange(0, 252)
            ev_spin.setValue(252 if key in ["hp", "attack", "sp_atk", "speed"] else 0)
            ev_spin.setFixedWidth(42); ev_spin.setFixedHeight(20)
            ev_spin.setStyleSheet(self._input_style())
            ev_spin.valueChanged.connect(self.calculate_stats)
            row_layout.addWidget(ev_spin)

            row_layout.addStretch()

            lbl_result = QLabel("0")
            lbl_result.setFixedWidth(42)
            lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_result.setStyleSheet("color: #3B82F6; font-size: 10px; font-weight: bold; border: none; background: #111116; border-radius: 3px;")
            row_layout.addWidget(lbl_result)

            self.stat_rows[key] = {
                "base": base_spin, 
                "iv": iv_spin, 
                "ev": ev_spin, 
                "result": lbl_result
            }
            st_layout.addWidget(row_frame)

        # Totals Summary Bar
        totals_frame = QFrame()
        totals_frame.setStyleSheet("background: #14141A; border: 1px solid #2E2E3C; border-radius: 5px;")
        t_layout = QHBoxLayout(totals_frame)
        t_layout.setContentsMargins(8, 4, 8, 4)
        
        t_layout.addWidget(QLabel("<b style='color: #A0A0B2; font-size: 10px;'>TOTALS:</b>"))
        t_layout.addStretch()
        self.total_base_lbl = QLabel("Base: 0")
        self.total_base_lbl.setStyleSheet("color: #D2D2E0; font-size: 10px; font-weight: bold; border: none;")
        t_layout.addWidget(self.total_base_lbl)
        
        t_layout.addWidget(QLabel("<span style='color: #444455;'>|</span>"))
        
        self.total_final_lbl = QLabel("Final: 0")
        self.total_final_lbl.setStyleSheet("color: #3B82F6; font-size: 10px; font-weight: bold; border: none;")
        t_layout.addWidget(self.total_final_lbl)

        st_layout.addWidget(totals_frame)
        c_outer_layout.addWidget(stats_calc_box)
        self.display_layout.addWidget(self.calc_widget)

        # Moves View Widget
        self.moves_widget = QWidget()
        m_layout = QVBoxLayout(self.moves_widget)
        m_layout.setContentsMargins(0, 0, 0, 0)
        moves_box = QGroupBox("Moves / Learnset")
        moves_box.setStyleSheet(self._box_style())
        mb_layout = QVBoxLayout(moves_box)
        mb_layout.setContentsMargins(2, 2, 2, 2)
        
        self.location_text_area = QTextEdit()
        self.location_text_area.setReadOnly(True)
        self.location_text_area.setFixedHeight(360)
        self.location_text_area.setStyleSheet("background: #141418; border: none; color: #E2E2E8; font-size: 11px;")
        mb_layout.addWidget(self.location_text_area)
        m_layout.addWidget(moves_box)
        self.moves_widget.setVisible(False)
        self.display_layout.addWidget(self.moves_widget)

        self.display_scroll.setWidget(self.display_container)
        self.c_layout.addWidget(self.display_scroll, 1)
        self.layout.addWidget(self.container)

        w, h = 480, 740
        if "pokedex_size" in self.main_app.config:
            saved_w, saved_h = self.main_app.config["pokedex_size"]
            w, h = max(420, saved_w), max(720, saved_h)
        self.resize(w, h)

        if "pokedex_pos" in self.main_app.config:
            x, y = self.main_app.config["pokedex_pos"]
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geo = screen.availableGeometry()
                x = max(screen_geo.x(), min(x, screen_geo.x() + screen_geo.width() - w))
                y = max(screen_geo.y(), min(y, screen_geo.y() + screen_geo.height() - h))
            self.move(x, y)
        else:
            self.apply_initial_position("pokedex_pos", default_rel_x=0.05, default_rel_y=0.15)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")
        self.load_pokemon_data(1)
        self.switch_view("calculator")

    @staticmethod
    def _box_style():
        return """
            QGroupBox { color: #8F8FA8; font-size: 10px; font-weight: bold; border: 1px solid #282836; border-radius: 6px; margin-top: 4px; padding-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
        """

    @staticmethod
    def _input_style():
        return """
            QSpinBox, QLineEdit {
                background-color: #111116; color: #E2E8F0;
                border: 1px solid #2E2E3D; border-radius: 4px;
                font-size: 9px; padding: 1px 3px;
            }
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; }
        """

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["pokedex_pos"] = [self.x(), self.y()]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)
        if hasattr(self, "main_app") and hasattr(self.main_app, "config"):
            self.main_app.config["pokedex_size"] = [self.width(), self.height()]

    def switch_view(self, mode):
        """
        Dynamically resizes window, sets strict minimum size bounds to 
        protect the stat calculator layout, and manages scrollbars.
        """
        if self.active_view == mode:
            self.active_view = None
            self.btn_view_calc.setChecked(False)
            self.btn_view_mov.setChecked(False)
            self.display_scroll.setVisible(False)
            self.setMinimumSize(420, 350)
            self.resize(self.width(), 350)
        else:
            self.active_view = mode
            self.btn_view_calc.setChecked(mode == "calculator")
            self.btn_view_mov.setChecked(mode == "moves")
            self.calc_widget.setVisible(mode == "calculator")
            self.moves_widget.setVisible(mode == "moves")
            self.display_scroll.setVisible(True)
            self.display_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            if mode == "calculator":
                self.setMinimumSize(420, 720)
                self.resize(self.width(), 740)
            elif mode == "moves":
                self.setMinimumSize(420, 480)
                self.resize(self.width(), 540)

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

    def calculate_stats(self):
        level = self.level_spin.value()
        nature_name = self.nature_input.text().strip().title()
        nature_info = self.get_nature_modifiers(nature_name)
        
        stat_full_names = {
            "hp": "HP", "attack": "Attack", "defense": "Defense",
            "sp_atk": "Special Attack", "sp_def": "Special Defense", "speed": "Speed"
        }

        total_base = 0
        total_final = 0

        for key, widgets in self.stat_rows.items():
            base = widgets["base"].value()
            iv = widgets["iv"].value()
            ev = widgets["ev"].value()

            total_base += base

            if key == "hp":
                if base == 1:
                    final_val = 1
                else:
                    ev_bonus = ev // 4
                    core = 2 * base + iv + ev_bonus
                    final_val = ((core * level) // 100) + level + 10
            else:
                ev_bonus = ev // 4
                core = 2 * base + iv + ev_bonus
                base_calc = ((core * level) // 100) + 5
                
                multiplier = 1.0
                full_name = stat_full_names.get(key)
                if nature_info.get("up") == full_name:
                    multiplier = 1.1
                elif nature_info.get("down") == full_name:
                    multiplier = 0.9

                final_val = math.floor(base_calc * multiplier)

            total_final += final_val
            widgets["result"].setText(f"{final_val}")

        self.total_base_lbl.setText(f"Base: {total_base}")
        self.total_final_lbl.setText(f"Final: {total_final}")

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

        stat_map_key = {
            "hp": "hp", 
            "attack": "attack", 
            "defense": "defense",
            "sp_attack": "sp_atk", 
            "special-attack": "sp_atk",
            "sp_defense": "sp_def", 
            "special-defense": "sp_def",
            "speed": "speed"
        }
        
        for s_key, val in stats.items():
            target_key = stat_map_key.get(s_key)
            if target_key and target_key in self.stat_rows:
                self.stat_rows[target_key]["base"].setValue(int(val))
        self.calculate_stats()

        evolutions = entry.get("evolutions", [])
        unique_evos = []
        for evo in evolutions:
            evo_name = evo.get("name") if isinstance(evo, dict) else str(evo)
            if evo_name and evo_name not in unique_evos:
                unique_evos.append(evo_name)
        evo_str = " ➔ ".join(unique_evos) if unique_evos else "None"

        self.load_sprite()
        
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

        self.name_lbl.setText(name_str)
        self.type_lbl.setText(types_str)
        self.ability_lbl.setText(f"Abilities: {abilities_str}")
        self.evo_lbl.setText(f"Evolution: {evo_str}")