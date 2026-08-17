<div align="center">

# PokePal

![Python](https://img.shields.io/badge/Python-3.14-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

*A lightweight, stand-alone desktop overlay application designed to enhance your PokeMMO experience by providing quick access to essential tools and calculators without needing to tab out of the game.*

## ✨ Features

**Pokédex:**  
*Search for any Pokémon to view base stats, abilities, evolutions, and move sets. You can also filter encounter locations—perfect for shiny hunts!*

**Easy Tracking:**  
*Customisable counters for tracking in-game stats like boxes sold or alphas caught. Simply use your mouse scroll wheel to adjust counts instantly.*

**Breeding Calculator:**  
*Fully simulate your egg outcomes by inputting the parents' information. Includes compatibility checks for the parents to ensure successful breeding.*

**Match-up Calculator:**  
*Select up to 2 types to instantly view damage multipliers, weaknesses, resistances, and immunities.*

**Timers:**  
*Fully customise and keep track of timed events like gym reruns, berry farming, and more.*

**Notepad:**  
*A simple notepad widget perfect for writing notes or even reading a guide without the need for multiple apps.*

</div>

<div align="center">

## 📸 Preview

<img width="100%" alt="PokePal Preview" src="https://github.com/user-attachments/assets/c210420a-ab66-4e6b-b981-842bc7704568" />

## 🚀 Installation & Setup

</div>

1. Head over to the repository **[Releases](releases)** page.
2. Download the latest `pokepal1.1.zip` and extract the folder to your computer.
3. Open the extracted folder `pokepal1.1`and double-click `pokepal1.1.exe` to launch the application.
Your all set!

>*Alternatively you can run from source (requires python 3.14 & pyQt6 installed)*

> ⚠️ **Important**  
> Ensure the `data` folder remains in the same directory as your `pokepal1.1.exe` The `config.json` configuration file will automatically generate on your first launch.

```
 📂 pokepal1.1/
├── 📂 data/ ........... (Sprites and info needed for the pokedex, matchup, and breeding calculators.)
├── 📄 pokepal1.1.exe .. (The app itself, compiled from source code using Pyinstaller.)
└── 📄 config.json ..... (Auto-saves your widget layout, sizes, and positions ready for your next session.)
```
---

<div align="center">

## 🧠 Why I Built It

</div>

> I was tired of constantly having to tab out of PokeMMO to check encounters, look up moves, calculate breeding stats, or losing track of hunts and timers.
> 
> The goal was to create a lightweight, community-friendly companion that puts everything you need right in one place without cluttering your screen, modifying game files, or risking your account. It is designed to keep you immersed in the game without needing multiple tabs open.

---

<div align="center">
    
## 🛡️ Safety & Technical Details

</div>

*PokePal is designed from the ground up to be **completely safe, independent, and compliant** with community standards:*

**Independent Companion:**  
*PokePal runs entirely as a separate application. It never hooks into the PokeMMO game client, reads system memory, or interferes with Windows processes.*

**Seamless Overlay UI:**  
*Built with PyQt6 to sit neatly on top of your desktop, ensuring all features and interactions are handled cleanly through standard mouse actions.*

**Local Storage:**  
*Your data stays yours. All configuration files, notes, and information are stored securely on your own machine via lightweight local JSON files.*
