## **Time-Constrained Travelling Christmas Market Visitor*

*Ant Colony Optimization (ACO) with Genetics, Pheromones & Multi-Day Logic*

This project implements an extended Ant Colony Optimization (ACO) framework to compute efficient routes through all Christmas markets in Vienna under strict time constraints (opening hours, walking/public transport times, daily limits).
The system combines:

* **Genetic inheritance (DNA)**
* **Pheromone-based reinforcement learning**
* **Multi-day exploration**
* **Google Maps travel-time preprocessing**

Ants are grouped into colonies, each starting from a different market. Over many generations, they improve their paths using crossover, selection, pheromone updates, and optional multi-day continuation. A full explanation of the methods used can be found in the accompanying report.

---

## **Project Structure**

```
src/
 ├── classes/
 │    ├── ant.py
 │    ├── ant_colony.py
 │    ├── ant_optimizer.py
 │    └── google_maps.py
 ├── main.py
 └── plots/                # created automatically
```

* **ant.py** — behaviour of a single ant
* **ant_colony.py** — selection, crossover, fitness evaluation
* **ant_optimizer.py** — coordinates all colonies, runs generations
* **google_maps.py** — reduced 170-edge map with travel times & pheromones
* **main.py** — contains the test configurations and experiment runner

---

## **How to Run**

### **1. Create a virtual environment**

```bash
python3 -m venv venv
```

### **2. Activate the environment**

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run the project**

Inside the activated environment:

```bash
python -m src.main
```

This will run the default experiment (`test_pure_pheromones_long()`), generate plots, and store them in:

```
/plots
```

### **5. To run the alternative test setups:**

Edit the last lines of `main.py`, for example:

```python
test_pure_DNA()
test_pure_pheromones()
test_hybrid()
test_pure_pheromones_long()
```

Uncomment whichever experiment you want.

---

## **Outputs**

Running the experiment generates:

* **Fitness curves**
* **Average and max visited markets per colony**
* **Best path graphs**
* **Final global best route**

All plots are saved into:

```
/plots
```

Additional visualisations are included in the report appendix.

---

## **Notes**

* All Google Maps data was preprocessed already — no API calls are made at runtime.
* The optimizer scales with number of ants, colonies, and days — long runs may take several minutes.