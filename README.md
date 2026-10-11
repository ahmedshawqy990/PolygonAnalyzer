# 📐 Irregular Polygon Area Analyzer

An interactive desktop application built with Python, Tkinter, and `ttkbootstrap` designed for analyzing irregular polygons, calculating precise surface areas using the Shoelace formula, sorting coordinates by angular orientation, and performing point-in-polygon containment tests.

---

## ✨ Features

* 🗺️ **Interactive Canvas & Pan/Zoom:** Dynamic cartesian coordinate system grid with smooth zooming and panning controls via mouse and buttons.
* 🔄 **Angular Point Sorting:** Automatically sorts input vertices around a calculated geometric centroid using `atan2` to prevent self-intersecting polygon shapes[cite: 9].
* 📏 **Precise Area Calculation:** Implements the Shoelace algorithm to compute exact polygon surface areas[cite: 9].
* 🔍 **Point-in-Polygon Testing:** Utilizes the Ray-casting algorithm to test whether a given coordinate point lies inside or outside the defined polygon[cite: 9].
* 💡 **Dynamic Theming:** Seamless light/dark mode toggling (`cosmo` and `superhero` themes)[cite: 9].
* 📝 **Step-by-Step Breakdown:** Detailed mathematical explanation window displaying intermediate Shoelace calculation terms and sums[cite: 9].

---

## 🛠️ Tech Stack

* **Language:** Python 3.x[cite: 9]
* **GUI Framework:** Tkinter, `ttkbootstrap`[cite: 9]
* **Math Utilities:** Python `math` module (Trigonometric functions, centroid sorting)[cite: 9]

---

## 📂 Project Structure

```text
PolygonAnalyzer/
│
├── POLYGON_Shawky.py   # Main GUI application and geometric analysis logic
└── README.md           # Project documentation