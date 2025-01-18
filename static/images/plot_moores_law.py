from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('dark_background')

plt.rc('font', size=20)
plt.rc('axes', titlesize=24)
plt.rc('axes', labelsize=24)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
plt.rc('ytick', labelsize=20)    # fontsize of the tick labels


# Data for transistor count
transistor_data = {
    1971: ("Intel 4004", 2300),
    1972: ("Intel 8008", 3500),
    1974: ("Intel 8080", 4500),
    1978: ("Intel 8086", 29000),
    1982: ("Intel 80286", 134000),
    1985: ("Intel 80386", 275000),
    1989: ("Intel 80486", 1200000),
    1993: ("Intel Pentium", 3100000),
    1997: ("Intel Pentium II", 7500000),
    1999: ("Intel Pentium III", 9500000),
    2000: ("Intel Pentium 4", 42000000),
    2006: ("Intel Core 2 Duo", 291000000),
    2008: ("Intel Core i7", 731000000),
    2012: ("Intel Core i7 3770K", 1400000000),
    2015: ("Intel Core i7 6700K", 1750000000),
    2017: ("AMD Ryzen Threadripper", 19200000000),
    2019: ("AMD Epyc Rome", 39540000000),
    2022: ("NVIDIA H100", 80000000000)
}

# Data for storage capacity (in GB)
storage_data = {
    1971: ("IBM 3330", 0.1),
    1980: ("Seagate ST-506", 2.52),
    1991: ("IBM 0663", 10),
    1998: ("IBM Deskstar 25GP", 47),
    2003: ("Hitachi Deskstar", 400),
    2005: ("Hitachi Deskstar", 500),
    2007: ("Hitachi Deskstar 7K1000", 1000),
    2010: ("Seagate Barracuda XT", 3000),
    2012: ("Hitachi Deskstar 7K4000", 4000),
    2014: ("Seagate Archive HDD", 8000),
    2016: ("Seagate BarraCuda Pro", 12000),
    2018: ("WD Ultrastar DC HC620", 15000),
    2020: ("Seagate IronWolf Pro", 20000),
    2022: ("Seagate Exos", 26000)
}

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16), sharex=True)
# Plot transistor count
years_t = list(transistor_data.keys())
transistors = [data[1] for data in transistor_data.values()]
ax1.semilogy(years_t, transistors, 'b-o', linewidth=4, markersize=12)
ax1.grid(True, which="both", ls="-", alpha=0.2)
ax1.set_ylabel('Transistorenzahl')

# Format transistor count y-axis labels
def format_transistors(x, p):
    if x >= 1e9:
        return f'{x/1e9:.1f}B'
    elif x >= 1e6:
        return f'{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'{x/1e3:.1f}K'
    return str(int(x))

ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_transistors))

# Plot storage capacity
years_s = list(storage_data.keys())
storage = [data[1] for data in storage_data.values()]
ax2.semilogy(years_s, storage, 'g-o', linewidth=4, markersize=12)
ax2.grid(True, which="both", ls="-", alpha=0.2)
ax2.set_xlabel('Jahr')
ax2.set_ylabel('Speicherkapazität')

# Format storage capacity y-axis labels
def format_storage(x, p):
    if x >= 1000:
        return f'{x/1000:.1f}TB'
    elif x >= 1:
        return f'{x:.1f}GB'
    return f'{x*1000:.0f}MB'

ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_storage))

# Set x-axis limits for both plots
ax1.set_xlim(1970, 2025)
ax2.set_xlim(1970, 2025)

# Save the plot
here = Path(__file__).parent
plt.savefig(here/'moores_law.png', dpi=300, bbox_inches='tight', transparent=True)
plt.close()
