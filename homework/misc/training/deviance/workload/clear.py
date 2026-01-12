import re
csv_file = "Q:\\Marcello\\University\\impianti\\impianti-di-elaborazione\\homework\\workload\\vmstat.csv"  
csv_out = "Q:\\Marcello\\University\\impianti\\impianti-di-elaborazione\\homework\\workload\\vmstat_clear.csv"  

with open(csv_file, "r") as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    # Replace multiple spaces within each line with a comma
    clean_line = re.sub(r' +', ',', line.strip())  # ' +' matches one or more spaces
    clean_lines.append(clean_line)
    
with open(csv_out, "w") as f:
    f.write("\n".join(clean_lines))
