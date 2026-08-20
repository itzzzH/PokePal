# widgets/breeding.py
import os
import json
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGroupBox, QSizeGrip, QCompleter, QTextEdit
)
from core.base_overlay import BaseOverlay
from globals import NATURES_LIST, BREEDING_ITEMS
import data_manager

class BreedingParentPanel(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.current_id = 1
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(4)

        top_h = QHBoxLayout()
        top_h.setSpacing(6)

        self.sprite_lbl = QLabel()
        self.sprite_lbl.setFixedSize(65, 65)
        self.sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_lbl.setStyleSheet("background: #141418; border: 1px solid #282832; border-radius: 4px;")
        top_h.addWidget(self.sprite_lbl)

        right_v = QVBoxLayout()
        right_v.setSpacing(3)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pokémon Name / #ID")
        if data_manager.POKEMON_NAMES_LIST:
            completer = QCompleter(data_manager.POKEMON_NAMES_LIST, self.search_input)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.activated.connect(self.on_completer_selected)
            self.search_input.setCompleter(completer)
        
        self.search_input.returnPressed.connect(self.perform_search)
        right_v.addWidget(self.search_input)

        nature_h = QHBoxLayout()
        nature_h.addWidget(QLabel("Nature:"))
        self.nature_input = QLineEdit()
        self.nature_input.setPlaceholderText("Nature name")
        if NATURES_LIST:
            nature_completer = QCompleter(NATURES_LIST, self.nature_input)
            nature_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            nature_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.nature_input.setCompleter(nature_completer)
        nature_h.addWidget(self.nature_input)
        right_v.addLayout(nature_h)

        gender_h = QHBoxLayout()
        gender_h.addWidget(QLabel("Gender:"))
        self.gender_input = QLineEdit()
        self.gender_input.setPlaceholderText("Male / Female / Genderless")
        gender_list = ["Male", "Female", "Genderless"]
        gender_completer = QCompleter(gender_list, self.gender_input)
        gender_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        gender_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.gender_input.setCompleter(gender_completer)
        gender_h.addWidget(self.gender_input)
        right_v.addLayout(gender_h)

        top_h.addLayout(right_v, 1)
        layout.addLayout(top_h)

        item_h = QHBoxLayout()
        item_h.addWidget(QLabel("Held Item:"))
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Held item name (Optional)")
        if BREEDING_ITEMS:
            item_completer = QCompleter(BREEDING_ITEMS, self.item_input)
            item_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            item_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.item_input.setCompleter(item_completer)
        item_h.addWidget(self.item_input)
        layout.addLayout(item_h)

        ivs_box = QGroupBox("Individual Values (IVs)")
        ivs_layout = QVBoxLayout(ivs_box)
        ivs_layout.setContentsMargins(6, 6, 6, 6)
        ivs_layout.setSpacing(3)

        self.iv_inputs = {}
        stat_map = [
            ("HP", "hp"), ("Attack", "attack"), ("Defense", "defense"),
            ("Sp. Atk", "spa"), ("Sp. Def", "spd"), ("Speed", "spe")
        ]
        
        for s_name, s_key in stat_map:
            row_h = QHBoxLayout()
            row_h.setSpacing(6)
            lbl = QLabel(s_name)
            lbl.setFixedWidth(55)
            lbl.setStyleSheet("color: #A0A0B0; font-size: 11px;")
            line_edit = QLineEdit("31")
            line_edit.setFixedHeight(22)
            line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_h.addWidget(lbl)
            row_h.addWidget(line_edit, 1)
            ivs_layout.addLayout(row_h)
            self.iv_inputs[s_key] = line_edit

        layout.addWidget(ivs_box)
        self.load_pokemon(1)

    def on_completer_selected(self, text):
        self.search_input.setText(text)
        self.perform_search()

    def perform_search(self):
        txt = self.search_input.text().strip()
        if not txt:
            return
        if txt.startswith("#"):
            txt = txt[1:]
        query_val = txt.split(" ")[0].lower()
        found_id = None
        if query_val.isdigit():
            found_id = int(query_val)
        else:
            entry = data_manager.MASTER_DEX_DB.get(query_val)
            if entry:
                found_id = int(entry.get("_clean_id", 1))
        if found_id:
            self.load_pokemon(found_id)

    def load_pokemon(self, poke_id):
        self.current_id = int(poke_id)
        entry = data_manager.MASTER_DEX_DB.get(str(self.current_id))
        name_val = entry.get("_clean_name", "Unknown") if entry else "Unknown"
        self.search_input.setText(f"#{self.current_id} {name_val}")

        if "ditto" in name_val.lower():
            self.gender_input.setText("Genderless")

        paths = [
            os.path.join("data", "sprites", f"{self.current_id}.png"),
            os.path.join("sprites", f"{self.current_id}.png"),
            f"{self.current_id}.png"
        ]
        pix = None
        for p in paths:
            if os.path.exists(p):
                pix = QPixmap(p)
                break
        if pix and not pix.isNull():
            self.sprite_lbl.setPixmap(pix.scaled(55, 55, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.sprite_lbl.setText("")
        else:
            self.sprite_lbl.setPixmap(QPixmap())
            self.sprite_lbl.setText("No Sprite")


class BreedingCalculatorWidget(BaseOverlay):
    def __init__(self, main_app):
        super().__init__("Breeding Calculator", main_app)
        self.egg_groups_db = self.load_egg_groups()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: #1E1E24; border-radius: 10px; border: 1px solid #363644; }
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(10, 10, 10, 10)
        c_layout.setSpacing(8)

        title_lbl = QLabel("🧬 Breeding Calculator")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        c_layout.addWidget(title_lbl)

        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(8)

        self.parent1 = BreedingParentPanel("Parent 1")
        self.parent2 = BreedingParentPanel("Parent 2")

        center_box = QGroupBox("egg")
        center_l = QVBoxLayout(center_box)
        center_l.setContentsMargins(6, 6, 6, 6)
        center_l.setSpacing(6)

        preview_h = QHBoxLayout()
        self.child_sprite_lbl = QLabel()
        self.child_sprite_lbl.setFixedSize(55, 55)
        self.child_sprite_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.child_sprite_lbl.setStyleSheet("background: #141418; border: 1px solid #282832; border-radius: 4px;")
        preview_h.addWidget(self.child_sprite_lbl)

        child_info_v = QVBoxLayout()
        self.child_name_lbl = QLabel("Child: —")
        self.child_name_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 12px; border: none;")
        child_info_v.addWidget(self.child_name_lbl)
        
        self.child_nature_lbl = QLabel("Nature: —")
        self.child_nature_lbl.setStyleSheet("color: #80A0FF; font-size: 11px; border: none;")
        child_info_v.addWidget(self.child_nature_lbl)
        preview_h.addLayout(child_info_v, 1)

        center_l.addLayout(preview_h)

        calc_btn = QPushButton("Calculate Offspring Odds")
        calc_btn.clicked.connect(self.calculate_breeding)
        center_l.addWidget(calc_btn)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet("background: #141418; border: none; color: #E2E2E8; font-size: 11px;")
        center_l.addWidget(self.result_area, 1)

        main_h_layout.addWidget(self.parent1, 1)
        main_h_layout.addWidget(center_box, 1)
        main_h_layout.addWidget(self.parent2, 1)

        c_layout.addLayout(main_h_layout)
        layout.addWidget(container)

        self.apply_initial_position("breeding_pos", default_rel_x=0.15, default_rel_y=0.20)

        if "breeding_size" in self.main_app.config:
            w, h = self.main_app.config["breeding_size"]
            self.resize(w, h)
        else:
            self.resize(760, 500)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background: transparent; width: 14px; height: 14px;")

    def load_egg_groups(self):
        paths = [
            os.path.join("data", "egg-groups-data.json"),
            os.path.join("egg-groups-data.json"),
            "egg_groups_data.json"
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    def get_pokemon_egg_groups(self, poke_id, poke_name):
        found_groups = []
        clean_name = poke_name.lower().strip()
        if clean_name.startswith("#"):
            parts = clean_name.split(" ", 1)
            if len(parts) > 1:
                clean_name = parts[1].strip()
            else:
                clean_name = clean_name.lstrip("#").strip()
        
        for group_key, group_data in self.egg_groups_db.items():
            if isinstance(group_data, dict):
                group_name = group_data.get("name", "")
                species_list = group_data.get("pokemon_species", [])
                for sp in species_list:
                    sp_name = sp.get("name", "").lower()
                    sp_url = sp.get("url", "")
                    sp_id = None
                    if sp_url:
                        parts = [p for p in sp_url.split("/") if p]
                        if parts and parts[-1].isdigit():
                            sp_id = int(parts[-1])
                    
                    if sp_name == clean_name or (sp_id and sp_id == int(poke_id)):
                        if group_name not in found_groups:
                            found_groups.append(group_name)
                        break
        return found_groups if found_groups else None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - 20, self.height() - 20)

    def calculate_breeding(self):
        p1_poke = self.parent1.search_input.text().strip()
        p2_poke = self.parent2.search_input.text().strip()
        p1_nat = self.parent1.nature_input.text().strip()
        p2_nat = self.parent2.nature_input.text().strip()
        g1 = self.parent1.gender_input.text().strip().capitalize()
        g2 = self.parent2.gender_input.text().strip().capitalize()

        is_p1_ditto = "ditto" in p1_poke.lower()
        is_p2_ditto = "ditto" in p2_poke.lower()

        valid_p1_gender = bool(g1) or is_p1_ditto
        valid_p2_gender = bool(g2) or is_p2_ditto

        if not p1_poke or not p2_poke or not p1_nat or not p2_nat or not valid_p1_gender or not valid_p2_gender:
            self.child_name_lbl.setText("Child: —")
            self.child_nature_lbl.setText("Nature: —")
            self.child_sprite_lbl.setPixmap(QPixmap())
            self.child_sprite_lbl.setText("Incomplete")
            self.result_area.setHtml(
                "<span style='color: #FF5555; font-weight: bold;'>⚠️ Incomplete Fields:</span><br>"
                "Please ensure Pokémon, Nature, and Gender (unless using Ditto) are fully completed for both parents before calculating."
            )
            return

        if is_p1_ditto and not g1:
            g1 = "Genderless"
        if is_p2_ditto and not g2:
            g2 = "Genderless"

        compatible = True
        compat_reason = ""

        if is_p1_ditto and is_p2_ditto:
            compatible = False
            compat_reason = "Two Dittos cannot breed together."
        elif is_p1_ditto or is_p2_ditto:
            other_parent = self.parent2 if is_p1_ditto else self.parent1
            other_poke = p2_poke if is_p1_ditto else p1_poke
            groups = self.get_pokemon_egg_groups(other_parent.current_id, other_poke)
            if groups:
                groups_lower = [str(g).lower() for g in groups]
                if any("undiscovered" in g or "no eggs" in g or "cannot-breed" in g for g in groups_lower):
                    compatible = False
                    compat_reason = "This Pokémon cannot breed (Undiscovered / Cannot-Breed group)."
            else:
                compatible = False
                compat_reason = "Could not verify egg groups for this Pokémon."
        else:
            if g1 == "Genderless" or g2 == "Genderless":
                compatible = False
                compat_reason = "Genderless Pokémon (other than Ditto) require Ditto to breed."
            elif g1 == g2:
                compatible = False
                compat_reason = "Parents have the same gender (must be opposite genders or include Ditto)."
            else:
                g_list1 = self.get_pokemon_egg_groups(self.parent1.current_id, p1_poke)
                g_list2 = self.get_pokemon_egg_groups(self.parent2.current_id, p2_poke)

                if g_list1 and g_list2:
                    g_list1_lower = [str(x).lower() for x in g_list1]
                    g_list2_lower = [str(x).lower() for x in g_list2]

                    if any("undiscovered" in x or "no eggs" in x or "cannot-breed" in x for x in g_list1_lower + g_list2_lower):
                        compatible = False
                        compat_reason = "One or both Pokémon are in the Unbreedable / Undiscovered group."
                    elif not set(g_list1_lower).intersection(set(g_list2_lower)):
                        compatible = False
                        compat_reason = "Parents do not share at least 1 compatible Egg Group."
                else:
                    compatible = False
                    compat_reason = "Could not verify egg groups for these Pokémon."

        if not compatible:
            self.child_name_lbl.setText("Child: Incompatible")
            self.child_nature_lbl.setText("Nature: —")
            self.child_sprite_lbl.setPixmap(QPixmap())
            self.child_sprite_lbl.setText("Invalid")
            self.result_area.setHtml(f"<span style='color: #FF5555; font-weight: bold;'>⚠️ Breeding Incompatible:</span><br>{compat_reason}")
            return

        if is_p1_ditto:
            target_parent = self.parent2
        elif is_p2_ditto:
            target_parent = self.parent1
        else:
            if g1 == "Female" and g2 == "Male":
                target_parent = self.parent1
            elif g2 == "Female" and g1 == "Male":
                target_parent = self.parent2
            else:
                target_parent = self.parent1

        child_id = target_parent.current_id
        entry = data_manager.MASTER_DEX_DB.get(str(child_id))
        child_name = entry.get("_clean_name", "Unknown") if entry else "Unknown"

        self.child_name_lbl.setText(f"Child: #{child_id} {child_name}")

        paths = [
            os.path.join("data", "sprites", f"{child_id}.png"),
            os.path.join("sprites", f"{child_id}.png"),
            f"{child_id}.png"
        ]
        pix = None
        for p in paths:
            if os.path.exists(p):
                pix = QPixmap(p)
                break
        if pix and not pix.isNull():
            self.child_sprite_lbl.setPixmap(pix.scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.child_sprite_lbl.setText("")
        else:
            self.child_sprite_lbl.setPixmap(QPixmap())
            self.child_sprite_lbl.setText("No Sprite")

        p1_item = self.parent1.item_input.text().strip()
        p2_item = self.parent2.item_input.text().strip()

        if "everstone" in p1_item.lower() and "everstone" not in p2_item.lower():
            offspring_nature = f"{p1_nat} (Guaranteed P1)"
        elif "everstone" in p2_item.lower() and "everstone" not in p1_item.lower():
            offspring_nature = f"{p2_nat} (Guaranteed P2)"
        elif "everstone" in p1_item.lower() and "everstone" in p2_item.lower():
            offspring_nature = f"50% {p1_nat} / 50% {p2_nat}"
        else:
            offspring_nature = "Random (No Everstone)"

        self.child_nature_lbl.setText(f"Nature: {offspring_nature}")

        stat_keys = ["hp", "attack", "defense", "spa", "spd", "spe"]
        stat_labels = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]

        p1_ivs = {}
        p2_ivs = {}
        for s in stat_keys:
            try:
                p1_ivs[s] = int(self.parent1.iv_inputs[s].text())
            except ValueError:
                p1_ivs[s] = 0
            try:
                p2_ivs[s] = int(self.parent2.iv_inputs[s].text())
            except ValueError:
                p2_ivs[s] = 0

        item_stat_map = {
            "power weight": "hp", "power bracer": "attack", "power belt": "defense",
            "power lens": "spa", "power band": "spd", "power anklet": "spe"
        }

        guaranteed_ivs = {}
        for k, st in item_stat_map.items():
            if k in p1_item.lower():
                guaranteed_ivs[st] = (p1_ivs[st], "Parent 1 Power Item")
            if k in p2_item.lower():
                guaranteed_ivs[st] = (p2_ivs[st], "Parent 2 Power Item")

        html_res = f"""
        <b>Inherited Nature:</b><br><span style='color: #80A0FF;'>{offspring_nature}</span><br><br>
        <b>Offspring Expected IVs (PokeMMO Rules):</b>
        <table width='100%' style='border-collapse: collapse; margin-top: 4px;'>
            <thead>
                <tr style='color: #80A0FF; text-align: left;'>
                    <th style='border-bottom: 1px solid #3E3E50;'>Stat</th>
                    <th style='border-bottom: 1px solid #3E3E50;'>P1</th>
                    <th style='border-bottom: 1px solid #3E3E50;'>P2</th>
                    <th style='border-bottom: 1px solid #3E3E50;'>Result / Odds</th>
                </tr>
            </thead>
            <tbody>
        """

        for idx, s_key in enumerate(stat_keys):
            s_label = stat_labels[idx]
            v1 = p1_ivs[s_key]
            v2 = p2_ivs[s_key]
            
            if s_key in guaranteed_ivs:
                val, _ = guaranteed_ivs[s_key]
                expected_str = f"<span style='color: #55FF55; font-weight: bold;'>{val} (Guaranteed Item)</span>"
            elif v1 == v2:
                expected_str = f"<span style='color: #55FF55; font-weight: bold;'>{v1} (Guaranteed Match)</span>"
            else:
                avg_val = int(round((v1 + v2) / 2.0))
                expected_str = f"<span style='color: #FFAA00;'>Range ({min(v1, v2)}-{max(v1, v2)}, ~{avg_val})</span>"

            html_res += f"""
                <tr style='border-bottom: 1px solid #282834;'>
                    <td style='padding: 2px; font-weight: bold; color: #90CDF4;'>{s_label}</td>
                    <td style='padding: 2px;'>{v1}</td>
                    <td style='padding: 2px;'>{v2}</td>
                    <td style='padding: 2px;'>{expected_str}</td>
                </tr>
            """
        html_res += "</tbody></table>"
        self.result_area.setHtml(html_res)