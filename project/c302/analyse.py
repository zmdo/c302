# =============================================================================
# 功能描述：
#   简易电压轨迹绘图脚本。
#   从 dat 格式仿真输出文件读取电压数据，绘制最多 302 个细胞的
#   膜电位轨迹叠加图（每条轨迹添加微小偏移以避免重叠）。
#
# 类与方法索引：
#   （脚本无函数定义）
#
# 更新日志：
#   2026-04-16  Copilot  添加中文行内注释
#
# 当前维护者：Copilot
# =============================================================================
import sys
import matplotlib.pyplot as plt


fig = plt.figure(facecolor="#FFFFFF", edgecolor="#FFFFFF")
p = fig.add_subplot(111)


dat_file = sys.argv[1]

traces = open(dat_file, "r")
volts = {}

# 效率较低的逐行解析方式
for line in traces:
    if not line.strip().startswith("#"):
        points = line.split()
        for i in range(len(points)):
            if not volts.has_key(i):
                volts[i] = []
            volts[i].append(float(points[i]) + 0.0020 * i)  # 每条轨迹添加微小偏移以避免重叠

for cell_index in volts.keys():
    if cell_index <= 302:  # 最多绘制 302 个细胞
        if cell_index > 0:
            p.plot(volts[0], volts[cell_index])

plt.show()
