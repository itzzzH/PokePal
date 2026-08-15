# 🐾 PokePal

![Python](https://img.shields.io/badge/Python-3.14-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

A lightweight, standalone desktop overlay application designed to enhance your PokeMMO experience by providing quick access to essential tools and calculators without needing to tab out of the game.

---

## ✨ Widgets

* **Pokédex:** Search for any Pokémon to view base stats, abilities, evolution lines, and learnsets. You can also filter encounter data by region, location, level, season, time of day, and type (Horde, Lure, etc.).
* **Easy Tracking:** Customizable counters for tracking in-game stats like boxes sold or alphas caught (use your mouse scroll wheel to adjust counts instantly).
* **Breeding Calculator:** Simulate breeding outcomes to calculate offspring stats, nature inheritance, and individual values (IVs).
* **Matchup Calculator:** Select types to instantly view damage multipliers, weaknesses, resistances, and immunities.
* **Timers:** Keep track of daily and hourly tasks like gym reruns and berry farming.
* **Notepad:** A quick sticky note for jotting down reminders on the fly.

---

## 📸 Preview

<img width="1911" height="1016" alt="PokePal Preview" src="https://github.com/user-attachments/assets/e6d20da0-6a24-496b-a399-db90727364c9" />

---

## 🧠 Why I Built It

> *I was tired of constantly having to tab out of PokeMMO to check encounters, look up moves, calculate breeding stats, or keep track of manual hunts and timers.*
> 
> *The goal was to create a lightweight, community-friendly companion that puts everything you need right in one place without cluttering your workflow, modifying game files, or risking your account. It is designed to keep you immersed in the game without needing multiple tabs open.*

---

## 🚀 Get Started

### Option 1: Run the Pre-Built Application (For Users)
1. Head over to the **[Releases](../../releases)** page of this repository.
2. Download the latest release `.zip` archive.
3. Extract the contents to a folder of your choice on your computer.
4. Double-click `pokepal.exe` to launch the application.

> **⚠️ Important:** Ensure the **`data/`** folder stays in the same directory right alongside `pokepal.exe`.

### Option 2: Run from Source (For Developers)
*(Requires Python 3.14 and PyQt6)*

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/pokepal.git](https://github.com/your-username/pokepal.git)
   cd pokepal
