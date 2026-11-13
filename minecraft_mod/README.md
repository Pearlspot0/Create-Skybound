# Create: Skybound

**Aeronautics Mooring, Sky Docks, Avionics & Fleet Logistics for Minecraft 1.21.1 (NeoForge)**  
*Engineered as a complimentary expansion for the latest **All of Create** (Aeronautics) modpack.*

---

## 🛩️ Overview

In the **All of Create** ecosystem, players construct monumental moving contraptions: massive cargo zeppelins, scout monoplanes, dreadnoughts, and ground locomotives. However, operating airborne fleets alongside stationary factories introduces critical logistical gaps:
- How do you safely berth a drifting 500-ton airship against a tower without collision damage?
- How do you navigate through low clouds, fog, and mountain ranges without GPS?
- How do you detect incoming hostile aircraft or long-range artillery shells from *Create: Big Cannons*?

**Create: Skybound** ties the entire modpack experience together by delivering industrial skyport mooring systems, real-time cockpit avionics, tactical early-warning airspace radar, extendable boarding gangways, and aeronautical brass materials.

---

## ⚙️ Core Features & Mechanics

### ⚓ 1. Mooring & Skyport Berthing Systems
* **Mooring Winch (`mooring_winch`)**: A motorized kinetic block that reels in attached vessels and mobile entities. When given redstone power, it reels in tethered airships toward the docking cradle, gently canceling drift.
* **Mooring Cleat (`mooring_cleat`)**: A compact brass anchor bollard placed on airship hulls and docking pylons.
* **High-Tensile Mooring Cable (`mooring_cable`)**: Right-click an anchor point and then a second cleat or winch (up to 48 blocks) to establish a physical tether with dynamic sag and particle effects. Sneak-click to release.
* **Pneumatic Docking Clamp (`docking_clamp`)**: An industrial magnetic/pneumatic docking lock. When activated, rigidly aligns and holds contraptions motionless in the docking bay. Emits Redstone comparator signal `15` when a vessel is securely docked.
* **Retractable Docking Gangway (`docking_gangway`)**: Extendable brass passenger and crew walkway. When powered or interacted with, deploys a solid walkway directly out to the airship hatchway so crew never plunge into the void.

---

### 🎛️ 2. Cockpit Avionics & Flight Instrumentation
* **Aero Altimeter Gauge (`altimeter_gauge`)**: Analog brass gauge displaying altitude relative to sea level (MSL) and world height (-64 to 320m). Outputs Redstone comparator signals proportional to altitude.
* **Variometer (`variometer_gauge`)**: Vertical speed indicator measuring rate of climb or descent (m/s). Crucial for preventing stall or ground collision during instrument flight.
* **Airspeed Indicator (`airspeed_gauge`)**: Measures horizontal velocity through the atmosphere.
* **Aeronaut Flight Visor (`aeronaut_visor`)**: Wearable aviator visor providing an in-game HUD overlay displaying compass heading (000°–359°), MSL altitude, vertical speed warning, and distance/bearing to the nearest Skyway Beacon.

---

### 📡 3. Skyway Navigation & Airspace Defense
* **Airspace Radar Console (`airspace_radar`)**: Early-warning sector radar with a phosphor-green cathode display. Scans a 64-block spherical airspace for moving aircraft, airborne players (elytra/jetpack), phantoms, and fast-moving artillery projectiles (such as *Big Cannons* shells).
  - Emits audio alerts and Redstone signals when contacts enter the perimeter.
  - Right-click for real-time tactical sector reports in chat!
* **Skyway Navigation Beacon (`skyway_beacon`)**: High-intensity aerial light beacon and radio transponder projecting vertical guidance beams. Can be colored using any vanilla dye.
* **Aeronaut's Flight Sextant (`flight_sextant`)**: Handheld navigation instrument. Right-click to calculate range, bearing, and altitude delta to the nearest Skyway Beacon in the dimension.
* **Airship IFF Transponder Key (`transponder_key`)**: Identity token for automated skyport clearance and traffic control.

---

### 🛡️ 4. Airframe Protection & Tactical Utilities
* **Padded Airship Bumper (`airship_bumper`)**: Quilted, reinforced bumper blocks for airship keels and docking docks. Completely negates kinetic collision damage and fall damage with a gentle damped rebound.
* **Ballast Thrust Vent (`ballast_vent`)**: High-pressure pneumatic jet vent that exhausts compressed air to lift airships or launch crew members.
* **Pneumatic Flare Gun & Parachute Signal Flares (`flare_gun`, `signal_flare`)**: Fires high-luminosity pyrotechnic flares that drift down on micro-parachutes, illuminating landing runways or marking targets for naval bombardments.
* **Aero-Brass Alloy (`aero_brass_ingot`, `aero_brass_sheet`, `aero_brass_casing`, `aero_brass_strut`)**: Lightweight aeronautical alloy framework with high blast resistance against cannon shrapnel and reduced weight for aeronautic flight physics.

---

## 🔧 Create & Modpack Compatibility

- **Create Wrench Support**: Right-clicking any Skybound block with Create's Wrench (or any item in `#c:tools/wrench`) rotates its orientation; sneak-right-clicking cleanly dismantles it.
- **Common Tags**: Fully registered under standard common tags (`#c:ingots/brass`, `#c:plates/brass`, `#minecraft:mineable/pickaxe`, etc.).
- **Soft Dependency Design**: Zero crash hazards if specific optional mods are updated or removed. Runs seamlessly both standalone and inside complete modpacks.

---

## 📦 Installation for "All of Create"

1. Ensure your modpack is running **Minecraft 1.21.1** with **NeoForge** (21.1.x).
2. Grab the pre-built jar file:
   - Located at: `build/libs/create_skybound-1.0.0.jar`
3. Drop `create_skybound-1.0.0.jar` into your modpack instance's `mods/` directory.
4. Launch and conquer the skies!

---

## 🛠️ Building From Source

```bash
./gradlew build
```
The compiled mod file is generated at `build/libs/create_skybound-1.0.0.jar`.
