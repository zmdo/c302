# =============================================================================
# 功能描述：
#   OpenWorm 赞助者细胞认领信息工具。
#   读取赞助者认领的细胞名称映射，生成 Markdown 格式的细胞信息页面，
#   包含细胞在 c302 网络文件中的位置链接和 3D 可视化链接。
#
# 类与方法索引：
#   get_adopted_cell_names               (L26)   — 读取 OpenWorm 赞助者认领的细胞名称映射
#
# 更新日志：
#   2026-04-16  Copilot  添加中文 docstring 和行内注释
#
# 当前维护者：Copilot
# =============================================================================
"""
This method reads a generated list of cells vs. names as assigned by OpenWorm backers

This information will eventually be moved to owmeta/elsewhere...
"""

import os

currentfile_dir = os.path.dirname(os.path.abspath(__file__))


def get_adopted_cell_names(root=os.path.join(currentfile_dir, "data")):
    """读取 OpenWorm 赞助者认领的细胞名称映射。

    从 ``data/adopters.txt`` 文件中解析 ``细胞名:认领名`` 格式的映射关系。

    :param root: 数据目录路径（默认为模块所在目录下的 ``data/``）
    :return: ``{细胞名: 认领名}`` 字典
    """
    with open(os.path.join(root, "adopters.txt")) as file:
        ads = {}  # {细胞名: 认领者名} 映射字典
        for line in file:
            cell = line.split(":")[0].strip()   # 冒号左侧为细胞名
            name = line.split(":")[1].strip()   # 冒号右侧为认领者名
            ads[cell] = name

    return ads


if __name__ == "__main__":
    ads = get_adopted_cell_names()

    file = open("cells.md", "w")

    info = ""

    info += "Cells which have been adopted in the OpenWorm project\n"
    info += "=====================================================\n\n"
    info += "The majority of these cells were sponsored by contributors during the Kickstarter campaign in 2014.\n\n"
    info += '<p align="center">\n'
    info += '  <img src="https://raw.githubusercontent.com/openworm/c302/experimental/images/SomeCells.png" alt="Some cells"/>\n'
    info += "</p>\n\n"

    url = (
        "https://github.com/openworm/c302/blob/master/examples/c302_C_Full.net.nml#L%i"
    )

    osb_3d_url = "https://v1.opensourcebrain.org/projects/c302/models?explorer=https%253A%252F%252Fraw.githubusercontent.com%252Fopenworm%252Fc302%252Fmaster%252Fc302%252FNeuroML2%252F"

    for cell in sorted(ads.keys()):
        name = ads[cell]
        info += cell + "\n"
        info += "----------\n\n"
        info += "Adopted name: **" + name + "**\n\n\n"
        i = 0
        search_file = open(
            os.path.normpath(
                os.path.join(currentfile_dir, "..", "examples", "c302_C_Full.net.nml")
            ),
            "r",
        )
        for line in search_file:
            i += 1
            if 'tag="OpenWormBackerAssignedName" value="%s"' % name in line:
                info += "Added to c302 network files [here](%s).\n\n" % (url % i)

        info += "This cell can be viewed in 3D [here](%s) (requires WebGL).\n\n" % (
            osb_3d_url + cell + ".cell.nml"
        )

    print(info)
    file.write(info)
    file.close()
