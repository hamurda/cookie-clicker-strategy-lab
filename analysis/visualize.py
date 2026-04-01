"""Generate comparison charts for the four cookie clicker strategies."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

C_GREEDY   = "#2196F3"
C_LLM      = "#FF9800"
C_CHEAPEST = "#4CAF50"
C_HYBRID   = "#E91E63"

BUILDING_COLORS = {
    "Cursor":       "#9E9E9E",
    "Grandma":      "#795548",
    "Farm":         "#8BC34A",
    "Mine":         "#607D8B",
    "Factory":      "#FF5722",
    "Bank":         "#FFC107",
    "Temple":       "#9C27B0",
    "Wizard Tower": "#3F51B5",
    "Shipment":     "#00BCD4",
    "Alchemy Lab":  "#E91E63",
}
UPGRADE_COLOR = "#F44336"

ts_greedy = [
    (100,7045123.15),(200,7045123.15),(300,7045123.15),(400,7045123.15),
    (500,7252216.48),(600,7252216.48),(700,7252216.48),(800,7252216.48),
    (900,7252216.48),(1000,7252216.48),(1100,7252216.48),(1200,7512216.48),
    (1300,7512216.48),(1400,7587845.28),(1500,7619580.91),(1600,7619580.91),
    (1700,7619580.91),(1800,7619580.91),(1900,7619580.91),(2000,7619580.91),
    (2100,7619580.91),(2200,7840597.76),(2300,7840597.76),(2400,7916476.16),
    (2500,7916476.16),(2600,7916476.16),(2700,7916476.16),(2800,7916476.16),
    (2900,7916476.16),(3000,7916476.16),(3100,7916476.16),(3200,8194497.84),
    (3300,8208749.84),(3400,8208749.84),(3500,8208749.84),(3600,8208749.84),
    (3700,8208749.84),(3800,8208749.84),(3900,8416723.17),(4000,8416723.17),
    (4100,8416723.17),(4200,8492726.37),(4300,8492726.37),(4400,8492726.37),
    (4500,8492726.37),(4600,8492726.37),(4700,8492726.37),(4800,8492726.37),
    (4900,8492726.37),(5000,8771218.13),
]

ts_llm = [
    (100,7091702.69),(200,7238439.76),(300,7262815.09),(400,7282654.83),
    (500,7282654.83),(600,7282654.83),(700,7282654.83),(800,7282654.83),
    (900,7282654.83),(1000,7490041.49),(1100,7490041.49),(1200,7490041.49),
    (1300,7490041.49),(1400,7490041.49),(1500,7490041.49),(1600,7490041.49),
    (1700,7764237.49),(1800,7771302.11),(1900,7771302.11),(2000,7847055.71),
    (2100,7847055.71),(2200,7847055.71),(2300,7847055.71),(2400,7847055.71),
    (2500,7847055.71),(2600,8054442.37),(2700,8054442.37),(2800,8054442.37),
    (2900,8054442.37),(3000,8054442.37),(3100,8054442.37),(3200,8054442.37),
    (3300,8314442.37),(3400,8314442.37),(3500,8314442.37),(3600,8314442.37),
    (3700,8314442.37),(3800,8314442.37),(3900,8314442.37),(4000,8314442.37),
    (4100,8314442.37),(4200,8314442.37),(4300,8314442.37),(4400,8314442.37),
    (4500,8314442.37),(4600,8314442.37),(4700,8314442.37),(4800,8314442.37),
    (4900,8314442.37),(5000,8314442.37),
]

ts_cheapest = [
    (100,7061002.24),(200,7069730.67),(300,7077931.73),(400,7083578.35),
    (500,7087810.72),(600,7092043.09),(700,7096275.47),(800,7099357.28),
    (900,7103325.97),(1000,7116645.71),(1100,7120625.09),(1200,7133958.08),
    (1300,7137944.96),(1400,7152172.16),(1500,7165546.40),(1600,7169543.97),
    (1700,7183799.17),(1800,7197214.67),(1900,7198380.27),(2000,7215502.93),
    (2100,7228692.80),(2200,7228962.88),(2300,7232981.84),(2400,7247289.84),
    (2500,7247293.04),(2600,7260791.04),(2700,7261964.16),(2800,7264820.69),
    (2900,7279156.69),(3000,7292426.51),(3100,7292699.15),(3200,7467370.61),
    (3300,7468547.49),(3400,7474274.43),(3500,7488638.43),(3600,7488641.63),
    (3700,7502378.08),(3800,7502652.00),(3900,7503832.64),(4000,7509573.44),
    (4100,7523965.44),(4200,7523968.64),(4300,7537752.00),(4400,7538027.20),
    (4500,7539211.60),(4600,7544966.27),(4700,7559386.27),(4800,7559389.47),
    (4900,7559389.47),(5000,7573219.73),
]

purchases_greedy = [
    (494,"buy_building","Wizard Tower"),(1197,"buy_building","Shipment"),
    (1400,"buy_building","Temple"),(1401,"buy_building","Cursor"),
    (1436,"buy_building","Grandma"),(1437,"buy_building","Farm"),
    (1444,"buy_building","Factory"),(1448,"buy_building","Mine"),
    (1491,"buy_building","Bank"),(2107,"buy_building","Wizard Tower"),
    (2147,"buy_building","Grandma"),(2370,"buy_building","Temple"),
    (3111,"buy_building","Shipment"),(3112,"buy_building","Cursor"),
    (3113,"buy_building","Farm"),(3121,"buy_building","Factory"),
    (3124,"buy_building","Mine"),(3168,"buy_building","Grandma"),
    (3214,"buy_building","Bank"),(3872,"buy_building","Wizard Tower"),
    (4111,"buy_building","Temple"),(4905,"buy_building","Shipment"),
    (4906,"buy_building","Cursor"),(4907,"buy_building","Farm"),
    (4915,"buy_building","Factory"),(4963,"buy_building","Grandma"),
    (4967,"buy_building","Mine"),
]

purchases_llm = [
    (1,"buy_upgrade","Factory grandma synergy"),(2,"buy_building","Factory"),
    (3,"buy_building","Factory"),(4,"buy_building","Factory"),
    (5,"buy_building","Bank"),(6,"buy_building","Mine"),
    (7,"buy_building","Mine"),(8,"buy_building","Farm"),
    (38,"buy_building","Grandma"),(39,"buy_building","Factory"),
    (51,"buy_building","Factory"),(51,"buy_building","Factory"),
    (66,"buy_building","Factory"),(83,"buy_building","Factory"),
    (175,"buy_upgrade","Factory tier 4"),(194,"buy_building","Factory"),
    (217,"buy_building","Factory"),(268,"buy_building","Bank"),
    (269,"buy_building","Farm"),(274,"buy_building","Mine"),
    (275,"buy_building","Farm"),(276,"buy_building","Cursor"),
    (277,"buy_building","Cursor"),(278,"buy_building","Cursor"),
    (281,"buy_building","Mine"),(282,"buy_building","Cursor"),
    (283,"buy_building","Cursor"),(284,"buy_building","Farm"),
    (285,"buy_building","Cursor"),(286,"buy_building","Cursor"),
    (287,"buy_building","Cursor"),(288,"buy_building","Farm"),
    (289,"buy_building","Mine"),(315,"buy_building","Factory"),
    (374,"buy_building","Bank"),(935,"buy_building","Wizard Tower"),
    (1616,"buy_building","Shipment"),(1680,"buy_building","Bank"),
    (1708,"buy_building","Factory"),(1715,"buy_building","Mine"),
    (1716,"buy_building","Farm"),(1717,"buy_building","Cursor"),
    (1912,"buy_building","Temple"),(2510,"buy_building","Wizard Tower"),
    (3239,"buy_building","Shipment"),
]

ts_hybrid = [
    (100,7094876.19),(200,7094876.19),(300,7170896.35),(400,7182183.81),
    (500,7330870.08),(600,7330870.08),(700,7330870.08),(800,7330870.08),
    (900,7330870.08),(1000,7330870.08),(1100,7538256.75),(1200,7538256.75),
    (1300,7538256.75),(1400,7538256.75),(1500,7538256.75),(1600,7538256.75),
    (1700,7538256.75),(1800,7812032.32),(1900,7812032.32),(2000,7812032.32),
    (2100,7812032.32),(2200,7812032.32),(2300,7812032.32),(2400,8019712.32),
    (2500,8019712.32),(2600,8019712.32),(2700,8019712.32),(2800,8019712.32),
    (2900,8019712.32),(3000,8019712.32),(3100,8279712.32),(3200,8279712.32),
    (3300,8355590.72),(3400,8369782.83),(3500,8369782.83),(3600,8369782.83),
    (3700,8369782.83),(3800,8369782.83),(3900,8369782.83),(4000,8577756.16),
    (4100,8577756.16),(4200,8577756.16),(4300,8577756.16),(4400,8577756.16),
    (4500,8577756.16),(4600,8577756.16),(4700,8577756.16),(4800,8837756.16),
    (4900,8837756.16),(5000,8913760.96),
]

purchases_hybrid = purchases = [
    (1,'buy_building','Bank'),
    (2,'buy_building','Factory'),
    (548,'buy_building','Wizard Tower'),
    (1249,'buy_building','Shipment'),
    (1258,'buy_building','Factory'),
    (1269,'buy_building','Factory'),
    (1281,'buy_building','Factory'),
    (1296,'buy_building','Factory'),
    (1312,'buy_building','Factory'),
    (1398,'buy_upgrade','Factory tier 4'),
    (1433,'buy_building','Grandma'),
    (1631,'buy_building','Temple'),
    (1632,'buy_building','Cursor'),
    (1633,'buy_building','Farm'),
    (1635,'buy_building','Mine'),
    (1675,'buy_building','Grandma'),
    (2278,'buy_building','Wizard Tower'),
    (3012,'buy_building','Shipment'),
    (3224,'buy_building','Temple'),
    (3225,'buy_building','Cursor'),
    (3226,'buy_building','Farm'),
    (3242,'buy_building','Factory'),
    (3285,'buy_building','Grandma'),
    (3288,'buy_building','Mine'),
    (3333,'buy_building','Bank'),
    (3979,'buy_building','Wizard Tower'),
    (4765,'buy_building','Shipment'),
    (4993,'buy_building','Temple'),
    (4994,'buy_building','Cursor'),
    (4995,'buy_building','Farm'),
]

inv_hybrid = [58, 109, 67, 58, 51, 41, 34, 21, 3, 0]

purchases_cheapest = [
    (1,"buy_building","Cursor"),(2,"buy_building","Cursor"),(3,"buy_building","Cursor"),
    (4,"buy_building","Cursor"),(5,"buy_building","Cursor"),(6,"buy_building","Cursor"),
    (7,"buy_building","Cursor"),(8,"buy_building","Cursor"),(9,"buy_building","Cursor"),
    (10,"buy_building","Cursor"),(11,"buy_building","Cursor"),(12,"buy_building","Cursor"),
    (13,"buy_building","Cursor"),(14,"buy_building","Cursor"),(15,"buy_building","Cursor"),
    (16,"buy_building","Cursor"),(17,"buy_building","Cursor"),(18,"buy_building","Cursor"),
    (19,"buy_building","Cursor"),(20,"buy_building","Cursor"),(21,"buy_building","Cursor"),
    (22,"buy_building","Cursor"),(23,"buy_building","Cursor"),(24,"buy_building","Cursor"),
    (25,"buy_building","Cursor"),(26,"buy_building","Cursor"),(27,"buy_building","Cursor"),
    (28,"buy_building","Cursor"),(29,"buy_building","Cursor"),(30,"buy_building","Cursor"),
    (31,"buy_building","Cursor"),(32,"buy_building","Cursor"),(33,"buy_building","Cursor"),
    (34,"buy_building","Cursor"),(35,"buy_building","Cursor"),(36,"buy_building","Cursor"),
    (37,"buy_building","Cursor"),(38,"buy_building","Farm"),(39,"buy_building","Cursor"),
    (40,"buy_building","Farm"),(41,"buy_building","Cursor"),(42,"buy_building","Farm"),
    (43,"buy_building","Cursor"),(44,"buy_building","Farm"),(45,"buy_building","Cursor"),
    (46,"buy_building","Farm"),(47,"buy_building","Cursor"),(48,"buy_building","Farm"),
    (49,"buy_building","Cursor"),(50,"buy_building","Farm"),(51,"buy_building","Cursor"),
    (52,"buy_building","Farm"),(53,"buy_building","Cursor"),(54,"buy_upgrade","Cursor tier 5"),
    (55,"buy_building","Farm"),(56,"buy_building","Cursor"),(57,"buy_building","Farm"),
    (58,"buy_building","Cursor"),(59,"buy_building","Farm"),(60,"buy_building","Cursor"),
    (61,"buy_building","Farm"),(62,"buy_building","Mine"),(63,"buy_building","Cursor"),
    (64,"buy_building","Farm"),(65,"buy_building","Mine"),(66,"buy_building","Cursor"),
    (67,"buy_building","Farm"),(68,"buy_building","Mine"),(69,"buy_building","Cursor"),
    (70,"buy_building","Farm"),(71,"buy_building","Mine"),(72,"buy_building","Cursor"),
    (73,"buy_building","Farm"),(74,"buy_building","Mine"),(75,"buy_building","Cursor"),
    (76,"buy_building","Farm"),(77,"buy_building","Mine"),(78,"buy_building","Cursor"),
    (79,"buy_building","Farm"),(80,"buy_building","Mine"),(82,"buy_building","Factory"),
    (91,"buy_building","Cursor"),(101,"buy_building","Farm"),(111,"buy_building","Mine"),
    (121,"buy_building","Factory"),(131,"buy_building","Cursor"),(142,"buy_building","Farm"),
    (153,"buy_building","Mine"),(165,"buy_building","Factory"),(176,"buy_building","Cursor"),
    (189,"buy_building","Farm"),(202,"buy_building","Mine"),(215,"buy_building","Factory"),
    (228,"buy_building","Cursor"),(243,"buy_building","Farm"),(258,"buy_building","Mine"),
    (273,"buy_building","Factory"),(289,"buy_building","Cursor"),(306,"buy_building","Farm"),
    (323,"buy_building","Mine"),(340,"buy_building","Factory"),(358,"buy_building","Cursor"),
    (377,"buy_building","Farm"),(397,"buy_building","Mine"),(417,"buy_building","Factory"),
    (437,"buy_building","Cursor"),(459,"buy_building","Farm"),(482,"buy_building","Mine"),
    (505,"buy_building","Factory"),(528,"buy_building","Cursor"),(554,"buy_building","Farm"),
    (580,"buy_building","Mine"),(606,"buy_building","Factory"),(633,"buy_building","Cursor"),
    (663,"buy_building","Farm"),(693,"buy_building","Mine"),(723,"buy_building","Factory"),
    (754,"buy_building","Cursor"),(788,"buy_building","Farm"),(822,"buy_building","Mine"),
    (857,"buy_building","Factory"),(892,"buy_building","Cursor"),(930,"buy_building","Grandma"),
    (969,"buy_building","Farm"),(1009,"buy_building","Mine"),(1049,"buy_building","Factory"),
    (1089,"buy_building","Cursor"),(1133,"buy_building","Grandma"),(1178,"buy_building","Farm"),
    (1223,"buy_building","Mine"),(1269,"buy_building","Factory"),(1314,"buy_building","Bank"),
    (1361,"buy_building","Cursor"),(1411,"buy_building","Grandma"),(1462,"buy_building","Farm"),
    (1514,"buy_building","Mine"),(1567,"buy_building","Factory"),(1619,"buy_building","Bank"),
    (1672,"buy_building","Cursor"),(1729,"buy_building","Grandma"),(1788,"buy_building","Farm"),
    (1848,"buy_building","Mine"),(1907,"buy_building","Factory"),(1967,"buy_building","Bank"),
    (2028,"buy_building","Cursor"),(2094,"buy_building","Grandma"),(2161,"buy_building","Farm"),
    (2229,"buy_building","Mine"),(2298,"buy_building","Factory"),(2366,"buy_building","Bank"),
    (2436,"buy_building","Cursor"),(2511,"buy_building","Grandma"),(2588,"buy_building","Farm"),
    (2666,"buy_building","Mine"),(2745,"buy_building","Factory"),(2823,"buy_building","Bank"),
    (2903,"buy_building","Cursor"),(2989,"buy_building","Grandma"),(3077,"buy_building","Farm"),
    (3166,"buy_upgrade","Factory tier 4"),(3254,"buy_building","Mine"),
    (3341,"buy_building","Factory"),(3429,"buy_building","Bank"),(3518,"buy_building","Cursor"),
    (3615,"buy_building","Grandma"),(3713,"buy_building","Farm"),(3813,"buy_building","Mine"),
    (3913,"buy_building","Factory"),(4014,"buy_building","Bank"),(4116,"buy_building","Cursor"),
    (4226,"buy_building","Grandma"),(4339,"buy_building","Farm"),(4453,"buy_building","Mine"),
    (4568,"buy_building","Factory"),(4683,"buy_building","Bank"),(4800,"buy_building","Cursor"),
    (4926,"buy_building","Grandma"),
]

BUILDINGS = ["Cursor","Grandma","Farm","Mine","Factory","Bank","Temple","Wizard Tower","Shipment","Alchemy Lab"]

inv_greedy   = [58, 110, 64, 58, 47, 41, 34, 21,  3, 0]
inv_llm      = [64, 107, 67, 61, 54, 43, 32, 20,  2, 0]
inv_cheapest = [129, 116, 98, 81, 64, 47, 31, 18, 0, 0]
inv_start    = [55, 106, 61, 55, 44, 39, 31, 18, 0, 0]

delta_greedy   = [inv_greedy[i]   - inv_start[i] for i in range(10)]
delta_llm      = [inv_llm[i]      - inv_start[i] for i in range(10)]
delta_cheapest = [inv_cheapest[i] - inv_start[i] for i in range(10)]
delta_hybrid   = [inv_hybrid[i]   - inv_start[i] for i in range(10)]


# Chart 1: CpS over time
fig1, ax1 = plt.subplots(figsize=(12, 6))

for ts, color, label in [
    (ts_greedy,   C_GREEDY,   "Greedy ROI"),
    (ts_llm,      C_LLM,      "LLM Planner"),
    (ts_cheapest, C_CHEAPEST, "Buy Cheapest"),
    (ts_hybrid,   C_HYBRID,   "Hybrid"),
]:
    ticks = [t for t, _ in ts]
    cps   = [c / 1e6 for _, c in ts]
    ax1.step(ticks, cps, where="post", color=color, linewidth=2, label=label)

ax1.set_xlabel("Tick (relative to game tick 35,000)")
ax1.set_ylabel("Cookies per Second (millions)")
ax1.set_title("CpS over Time — Three Strategies")
ax1.legend()
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}M"))
ax1.grid(axis="y", alpha=0.3)
fig1.tight_layout()
fig1.savefig("results/chart_cps_over_time.png", dpi=150)
print("Saved results/chart_cps_over_time.png")


# Chart 2: Purchase timeline
fig2, axes = plt.subplots(4, 1, figsize=(14, 8), sharex=True)

strategy_data = [
    (purchases_greedy,   C_GREEDY,   "Greedy ROI",   axes[0]),
    (purchases_llm,      C_LLM,      "LLM Planner",  axes[1]),
    (purchases_cheapest, C_CHEAPEST, "Buy Cheapest",  axes[2]),
    (purchases_hybrid,   C_HYBRID,   "Hybrid",        axes[3]),
]

for purchases, strat_color, strat_label, ax in strategy_data:
    for tick, kind, target in purchases:
        if kind == "buy_upgrade":
            color = UPGRADE_COLOR
            marker = "*"
            size = 120
        else:
            color = BUILDING_COLORS.get(target, "#9E9E9E")
            marker = "o"
            size = 40
        ax.scatter(tick, 0, c=color, marker=marker, s=size, zorder=3, linewidths=0)

    ax.set_ylabel(strat_label, rotation=0, ha="right", va="center", labelpad=60,
                  color=strat_color, fontweight="bold")
    ax.set_yticks([])
    ax.set_ylim(-0.5, 0.5)
    ax.axhline(0, color="#cccccc", linewidth=0.8, zorder=1)
    ax.grid(axis="x", alpha=0.2)

axes[3].set_xlabel("Tick (relative to game tick 35,000)")
fig2.suptitle("Purchase Timeline — When Each Strategy Bought What", y=1.01)

legend_handles = []
for name, color in BUILDING_COLORS.items():
    legend_handles.append(mpatches.Patch(color=color, label=name))
legend_handles.append(plt.Line2D([0],[0], marker="*", color="w", markerfacecolor=UPGRADE_COLOR,
                                  markersize=10, label="Upgrade"))
fig2.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(1.13, 1.0),
            fontsize=8, title="Purchase type", title_fontsize=8)

fig2.tight_layout()
fig2.savefig("results/chart_purchase_timeline.png", dpi=150, bbox_inches="tight")
print("Saved results/chart_purchase_timeline.png")


# Chart 3: Final building inventory (delta from start)
fig3, ax3 = plt.subplots(figsize=(13, 6))

x = np.arange(len(BUILDINGS))
width = 0.2

bars_g = ax3.bar(x - 1.5*width, delta_greedy,   width, label="Greedy ROI",  color=C_GREEDY)
bars_l = ax3.bar(x - 0.5*width, delta_llm,      width, label="LLM Planner", color=C_LLM)
bars_c = ax3.bar(x + 0.5*width, delta_cheapest, width, label="Buy Cheapest", color=C_CHEAPEST)
bars_h = ax3.bar(x + 1.5*width, delta_hybrid,   width, label="Hybrid",       color=C_HYBRID)

ax3.set_xlabel("Building type")
ax3.set_ylabel("Buildings purchased during run")
ax3.set_title("Buildings Purchased per Strategy (5,000-tick run)")
ax3.set_xticks(x)
ax3.set_xticklabels(BUILDINGS, rotation=20, ha="right")
ax3.legend()
ax3.grid(axis="y", alpha=0.3)

for bars in (bars_g, bars_l, bars_c, bars_h):
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax3.text(bar.get_x() + bar.get_width() / 2, h + 0.3, str(int(h)),
                     ha="center", va="bottom", fontsize=7)

fig3.tight_layout()
fig3.savefig("results/chart_building_inventory.png", dpi=150)
print("Saved results/chart_building_inventory.png")
