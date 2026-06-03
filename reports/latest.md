# RA Signal Agent Report — 2026-06-03

**Global state:** `critical`  
**Global severity:** 90/100

| Domain | Sources | OK | Negative space | Max severity |
|---|---:|---:|---:|---:|
| banking_cre | 3 | 1 | 2 | 85 |
| food | 3 | 3 | 0 | 90 |
| water | 3 | 2 | 1 | 85 |
| critical_minerals | 2 | 2 | 0 | 90 |
| institutional_trust | 2 | 0 | 2 | 25 |
| supply_chain | 1 | 0 | 1 | 25 |
| civil_unrest | 1 | 0 | 1 | 25 |

## Observations

| Signal | Domain | Status | State | Severity | Evidence |
|---|---|---|---|---:|---|
| `fred_financial_stress_stlfsi4` | banking_cre | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `fred_cre_delinquency_all_banks` | banking_cre | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `federal_reserve_stress_test_watch` | banking_cre | ok | critical | 85 | nd Communications Overview Supervision & Regulation Supervision Community Banks Regional Banks and Foreign Banks with U.S. Assets Large Banks and Large Foreign Banks Global Systemi |
| `fao_food_price_index_watch` | food | ok | critical | 85 | FAO Food Price Index \| Food and Agriculture Organization of the United Nations Discover About FAO News Multimedia Main topics Statistics Members Publications English العربية 中文 Fr |
| `world_bank_commodities_food_watch` | food | ok | critical | 85 |  6.1% increase in U.S. natural gas prices. The non-energy index rose 2.5%, with food prices up 1.9% while fertilizer prices eased 4.3%. Beverage prices increased 5.3%, and raw mate |
| `gdelt_food_shortage_watch` | food | ok | critical | 90 | GDELT query=("food shortage" OR "food crisis" OR "food price inflation" OR "fertilizer shortage") timespan=7d |
| `us_drought_monitor_data_watch` | water | ok | critical | 85 | Data Download \| U.S. Drought Monitor --> U.S. Drought Monitor Current Maps Compare Two Weeks Comparison Slider Map Archive Map Areas Map Types Map Viewer Change Maps Animations Ex |
| `nasa_grace_groundwater_watch` | water | ok | critical | 85 |  long-term trends and mean seasonal amplitudes! ALL DATA Applications Hydrology Groundwater is a useful indicator of climate variability and human impacts on the environment. Land  |
| `gdelt_water_shortage_watch` | water | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `usgs_mineral_commodity_summaries_watch` | critical_minerals | ok | monitor | 5 | Mineral Commodity Summaries \| U.S. Geological Survey Skip to main content An official website of the United States government Here's how you know Here's how you know Official webs |
| `gdelt_copper_lithium_shortage_watch` | critical_minerals | ok | critical | 90 | GDELT query=("copper shortage" OR "lithium deficit" OR "critical minerals shortage" OR "battery minerals shortage") timespan=7d |
| `pew_public_trust_watch` | institutional_trust | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `gdelt_polarization_legitimacy_watch` | institutional_trust | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `gdelt_supply_chain_disruption_watch` | supply_chain | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |
| `gdelt_civil_unrest_watch` | civil_unrest | error | negative_space | 25 | Source unavailable/unparsable; recorded as negative space. |