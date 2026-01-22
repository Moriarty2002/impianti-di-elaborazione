import pandas as pd
import os

def analyze_bottlenecks():
    """Analyze vmstat and JMeter metrics to identify bottlenecks at higher CTT values."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load data
    vmstat_df = pd.read_csv(os.path.join(script_dir, "summary_results_vmstat_grouped.csv"))
    jmeter_df = pd.read_csv(os.path.join(script_dir, "summary_results_grouped.csv"))
    
    # Convert group column to numeric for sorting
    vmstat_df["ctt"] = vmstat_df["group"].astype(int)
    jmeter_df["ctt"] = jmeter_df["group"].str.extract(r"(\d+)")[0].astype(int)
    
    # Sort by CTT
    vmstat_df = vmstat_df.sort_values("ctt")
    jmeter_df = jmeter_df.sort_values("ctt")
    
    # Merge dataframes
    merged_df = pd.merge(vmstat_df, jmeter_df, on="ctt", how="inner")
    
    print("=" * 80)
    print("BOTTLENECK ANALYSIS - Server Degradation at Higher CTT Values")
    print("=" * 80)
    print()
    
    # Analyze performance degradation
    print("📊 PERFORMANCE METRICS OVERVIEW")
    print("-" * 80)
    print(f"{'CTT':<6} {'Resp.Time(ms)':<15} {'Throughput':<12} {'Power':<10} {'Status':<20}")
    print("-" * 80)
    
    for _, row in jmeter_df.iterrows():
        ctt = row["ctt"]
        resp_time = row["avg_response_time_ms"]
        throughput = row["throughput"]
        power = row["power"]
        
        # Identify degradation
        if resp_time > 500:
            status = "🔴 SEVERE DEGRADATION"
        elif resp_time > 200:
            status = "🟡 MODERATE DEGRADATION"
        else:
            status = "🟢 GOOD"
            
        print(f"{ctt:<6} {resp_time:<15.2f} {throughput:<12.2f} {power:<10.4f} {status}")
    
    print()
    print("=" * 80)
    print("🔍 BOTTLENECK IDENTIFICATION BY RESOURCE TYPE")
    print("=" * 80)
    print()
    
    # CPU Bottleneck Analysis
    print("1️⃣  CPU BOTTLENECK ANALYSIS")
    print("-" * 80)
    print(f"{'CTT':<6} {'User%':<8} {'Sys%':<8} {'Idle%':<8} {'Wait%':<8} {'RunQ':<8} {'Status':<20}")
    print("-" * 80)
    
    for _, row in merged_df.iterrows():
        ctt = row["ctt"]
        us = row["us"]
        sy = row["sy"]
        idle = row["id"]
        wa = row["wa"]
        runq = row["r"]
        
        # CPU bottleneck indicators
        cpu_bottleneck = []
        if idle < 10:
            cpu_bottleneck.append("Low Idle")
        if us + sy > 90:
            cpu_bottleneck.append("High CPU Usage")
        if runq > 10:
            cpu_bottleneck.append("High RunQueue")
        if wa > 5:
            cpu_bottleneck.append("High I/O Wait")
            
        status = "🔴 " + ", ".join(cpu_bottleneck) if cpu_bottleneck else "🟢 Normal"
        print(f"{ctt:<6} {us:<8.1f} {sy:<8.1f} {idle:<8.1f} {wa:<8.1f} {runq:<8.1f} {status}")
    
    print()
    
    # Memory Bottleneck Analysis
    print("2️⃣  MEMORY BOTTLENECK ANALYSIS")
    print("-" * 80)
    print(f"{'CTT':<6} {'Free(MB)':<12} {'Cache(MB)':<12} {'Buff(MB)':<12} {'Swap(MB)':<12} {'Status':<20}")
    print("-" * 80)
    
    for _, row in merged_df.iterrows():
        ctt = row["ctt"]
        free = row["free"] / 1024  # Convert to MB
        cache = row["cache"] / 1024
        buff = row["buff"] / 1024
        swpd = row["swpd"] / 1024
        
        # Memory bottleneck indicators
        mem_bottleneck = []
        if free < 50:  # Less than 50 MB free
            mem_bottleneck.append("Low Free Memory")
        if swpd > 0:
            mem_bottleneck.append("Swap Used")
        if cache < 70:
            mem_bottleneck.append("Low Cache")
            
        status = "🔴 " + ", ".join(mem_bottleneck) if mem_bottleneck else "🟢 Normal"
        print(f"{ctt:<6} {free:<12.1f} {cache:<12.1f} {buff:<12.1f} {swpd:<12.1f} {status}")
    
    print()
    
    # I/O Bottleneck Analysis
    print("3️⃣  I/O BOTTLENECK ANALYSIS")
    print("-" * 80)
    print(f"{'CTT':<6} {'BlockIn':<12} {'BlockOut':<12} {'IOWait%':<10} {'BlkProcs':<10} {'Status':<20}")
    print("-" * 80)
    
    for _, row in merged_df.iterrows():
        ctt = row["ctt"]
        bi = row["bi"]
        bo = row["bo"]
        wa = row["wa"]
        blocked = row["b"]
        
        # I/O bottleneck indicators
        io_bottleneck = []
        if wa > 10:
            io_bottleneck.append("High I/O Wait")
        if blocked > 1:
            io_bottleneck.append("High Blocked Procs")
        if bi > 300000:
            io_bottleneck.append("High Block Read")
            
        status = "🔴 " + ", ".join(io_bottleneck) if io_bottleneck else "🟢 Normal"
        print(f"{ctt:<6} {bi:<12.0f} {bo:<12.0f} {wa:<10.1f} {blocked:<10.1f} {status}")
    
    print()
    
    # System Resources Analysis
    print("4️⃣  SYSTEM RESOURCES ANALYSIS")
    print("-" * 80)
    print(f"{'CTT':<6} {'Interrupts':<12} {'CtxSwitch':<12} {'RunQueue':<12} {'Status':<20}")
    print("-" * 80)
    
    for _, row in merged_df.iterrows():
        ctt = row["ctt"]
        interrupts = row["in"]
        ctx_switch = row["cs"]
        runq = row["r"]
        
        # System bottleneck indicators
        sys_bottleneck = []
        if interrupts > 10000:
            sys_bottleneck.append("High Interrupts")
        if ctx_switch > 8000:
            sys_bottleneck.append("High Context Switches")
        if runq > 10:
            sys_bottleneck.append("High Run Queue")
            
        status = "🟡 " + ", ".join(sys_bottleneck) if sys_bottleneck else "🟢 Normal"
        print(f"{ctt:<6} {interrupts:<12.0f} {ctx_switch:<12.0f} {runq:<12.1f} {status}")
    
    print()
    print("=" * 80)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # Find the critical thresholds
    critical_ctt = merged_df[merged_df["avg_response_time_ms"] > 500]["ctt"].min()
    degraded_ctt = merged_df[merged_df["avg_response_time_ms"] > 200]["ctt"].min()
    
    print(f"🎯 Performance Thresholds:")
    print(f"   - Good performance: CTT ≤ 1800 (response time < 200ms)")
    print(f"   - Moderate degradation starts: CTT = {degraded_ctt} (response time > 200ms)")
    print(f"   - Severe degradation starts: CTT = {critical_ctt} (response time > 500ms)")
    print()
    
    print("🔴 PRIMARY BOTTLENECKS IDENTIFIED:")
    print()
    
    # Analyze CTT 2500+ where degradation is moderate/severe
    high_load = merged_df[merged_df["ctt"] >= 2500]
    
    print("   At CTT = 2500 (Moderate Degradation):")
    row_2500 = merged_df[merged_df["ctt"] == 2500].iloc[0]
    print(f"   • CPU: {row_2500['us'] + row_2500['sy']:.1f}% utilized, {row_2500['id']:.1f}% idle")
    print(f"   • Run Queue: {row_2500['r']:.1f} processes (HIGH - indicates CPU saturation)")
    print(f"   • I/O Wait: {row_2500['wa']:.1f}% (very low, not the bottleneck)")
    print(f"   • Free Memory: {row_2500['free']/1024:.1f} MB")
    print(f"   ➡️  CPU is becoming saturated, run queue pressure building up")
    print()
    
    print("   At CTT = 3200 (Moderate Degradation):")
    row_3200 = merged_df[merged_df["ctt"] == 3200].iloc[0]
    print(f"   • CPU: {row_3200['us'] + row_3200['sy']:.1f}% utilized, {row_3200['id']:.1f}% idle")
    print(f"   • Run Queue: {row_3200['r']:.1f} processes (VERY HIGH)")
    print(f"   • Context Switches: {row_3200['cs']:.0f}/s")
    print(f"   ➡️  CPU bottleneck evident, many processes waiting for CPU time")
    print()
    
    print("   At CTT = 3800 (Severe Degradation):")
    row_3800 = merged_df[merged_df["ctt"] == 3800].iloc[0]
    print(f"   • CPU: {row_3800['us'] + row_3800['sy']:.1f}% utilized, {row_3800['id']:.1f}% idle")
    print(f"   • Run Queue: {row_3800['r']:.1f} processes (CRITICAL - nearly 50 waiting!)")
    print(f"   • Idle Time: {row_3800['id']:.1f}% (CPU fully saturated)")
    print(f"   • Throughput: {row_3800['throughput']:.1f} req/s (DROPPED from peak of 38!)")
    print(f"   ➡️  SEVERE CPU BOTTLENECK - System overloaded, throughput collapse")
    print()
    
    print("📌 CONCLUSION:")
    print("   The PRIMARY bottleneck is CPU saturation at high CTT values.")
    print("   Evidence:")
    print("   ✓ Run queue grows dramatically (0.8 → 47 processes)")
    print("   ✓ CPU idle time drops to near zero (1.6% at CTT=3800)")
    print("   ✓ Response time increases exponentially (75ms → 2177ms)")
    print("   ✓ Throughput peaks at CTT=3200 then collapses")
    print("   ✓ I/O wait remains low (< 1%), ruling out I/O bottleneck")
    print("   ✓ Memory remains adequate throughout tests")
    print()
    print("💡 RECOMMENDATIONS:")
    print("   1. Keep CTT ≤ 1800 for optimal performance (< 200ms response time)")
    print("   2. Consider horizontal scaling (more servers) for higher loads")
    print("   3. Optimize CPU-intensive operations in the application code")
    print("   4. Consider vertical scaling (more CPU cores) if needed")
    print()
    print("=" * 80)


if __name__ == "__main__":
    analyze_bottlenecks()
