# =============================================================================
# 功能描述：
#   通过 owmeta 语义知识图谱框架读取线虫神经元连接数据的数据读取器。
#   原作者：Mark Watts（github.com/mwatts15）。封装 Bundle 查询逻辑并
#   缓存结果，提供与其他数据读取器一致的 read_data() 和 read_muscle_data() 接口。
#
# 类与方法索引：
#   OpenWormReader                       (L48)   — 封装 owmeta Bundle 查询接口的连接组数据读取器
#     __init__                           (L56)   — __init__ 函数
#     get_cells_in_model                 (L60)   — 提取 owmeta 神经网络对象中所有神经元的名称集合
#     read_data                          (L73)   — 读取神经元间连接数据
#     read_muscle_data                   (L98)   — 读取神经肌肉连接数据
#     _read_connections                  (L109)  — 内部方法：执行 owmeta Bundle 查询并返回连接列表
#   format_muscle_name                   (L192)  — 将 owmeta 返回的肌肉名称转换为 c302 标准命名格式
#
# 更新日志：
#   2026-04-16  zmdo  添加中文注释（计划1 阶段二）
#
# 当前维护者：zmdo
# =============================================================================
import logging
import re

from c302.ConnectomeReader import ConnectionInfo
from c302.ConnectomeReader import analyse_connections
from c302 import print_, MUSCLE_RE

try:
    from owmeta_core.bundle import Bundle
    from owmeta_core.context import Context
    from owmeta.neuron import Neuron
    from owmeta.muscle import BodyWallMuscle
    from owmeta.worm import Worm
except Exception:
    print("owmeta not installed! Cannot run OpenWormReader")
    exit()

############################################################

#   读取 owmeta 项目数据库中神经元连接数据的简单脚本
#   原作者：Mark Watts（github.com/mwatts15）

############################################################

LOGGER = logging.getLogger(__name__)


class OpenWormReader(object):
    """封装 owmeta Bundle 查询接口的连接组数据读取器。

    实现与其他数据读取器相同的 read_data/read_muscle_data 接口，
    将 owmeta 语义知识图谱查询结果转换为 ConnectionInfo 对象列表。
    """

    # 封装 owmeta Bundle 查询接口，实现和其他数据读取器相同的 read_data/read_muscle_data 接口
    def __init__(self):
        # 缓存标志：True 表示已执行过 Bundle 查询，后续调用直接使用缓存数据
        self.cached = False

    def get_cells_in_model(self, net):
        """提取 owmeta 神经网络对象中所有神经元的名称集合。

        :param net: owmeta NeuronNetwork 对象
        :return: 神经元名称字符串集合
        """
        # 提取神经网络中所有神经元的名称集合
        cell_names = set()
        for n in net.neurons():
            cell_names.add(str(n.name()))

        return cell_names

    def read_data(self, include_nonconnected_cells=False):
        """读取神经元间连接数据。

        :param include_nonconnected_cells: 为 True 时将无连接神经元也加入返回列表
        :return: 元组 (cells, conns)
                 - cells: 神经元名称列表
                 - conns: ConnectionInfo 连接对象列表
        """
        print_("Initialising OpenWormReader")

        try:
            cell_names, pre, post, conns = self._read_connections("neuron")
        except Exception:
            print(
                "\nProblem loading connections via owmeta! The package is installed however. You may need to try running:"
                + "\n\n    owm bundle remote --user add ow 'https://raw.githubusercontent.com/openworm/owmeta-bundles/master/index.json'\n"
            )

            exit()

        if include_nonconnected_cells:
            return cell_names, conns
        else:
            return pre + post, conns

    def read_muscle_data(self):
        """读取神经肌肉连接数据。

        :return: 元组 (neurons, muscles, conns)
                 - neurons: 有肌肉连接的运动神经元名称列表
                 - muscles: 肌肉细胞名称列表
                 - conns: 神经肌肉 ConnectionInfo 连接对象列表
        """
        cell_names, neurons, muscles, conns = self._read_connections("muscle")
        return neurons, muscles, conns

    def _read_connections(self, termination=None):
        """内部方法：执行 owmeta Bundle 查询并返回连接列表。

        :param termination: 过滤类型，'neuron' / 'muscle' / None（全部）
        :return: 元组 (cell_names_list, pre_cell_names, post_cell_names, conns)
        """
        # 如果没有缓存，执行 Bundle 查询并缓存结果
        if not self.cached:
            with Bundle("openworm/owmeta-data", version=6) as bnd:
                ctx = bnd(Context)(ident="http://openworm.org/data").stored
                # 从虫对象获取神经网络对象
                net = ctx(Worm).query().neuron_network()

                syn = net.synapse.expr
                pre = syn.pre_cell
                post = syn.post_cell

                (pre | post).rdf_type(multiple=True)

                # 预加载所有需要的属性，降低后续遍历时的查询次数
                (pre | post).name()
                pre()
                post()
                syn.syntype()
                syn.synclass()
                syn.number()
                # 将所有穑触对象转换为 Python对象列表并缓存
                self.connlist = syn.to_objects()

                self.cell_names = self.get_cells_in_model(net)
            self.cached = True

        # 根据 termination 过滤连接类型：neuron-only、muscle-only 或全部
        if termination == "neuron":
            term_type = set([Neuron.rdf_type])
        elif termination == "muscle":
            term_type = set([BodyWallMuscle.rdf_type])
        else:
            term_type = set([Neuron.rdf_type, BodyWallMuscle.rdf_type])

        conns = []
        pre_cell_names = set()
        post_cell_names = set()
        for conn in self.connlist:
            if Neuron.rdf_type in conn.pre_cell.rdf_type and term_type & set(
                conn.post_cell.rdf_type
            ):
                num = conn.number
                syntype = conn.syntype or ""
                synclass = conn.synclass or ""
                pre_name = conn.pre_cell.name
                post_name = conn.post_cell.name
                if BodyWallMuscle.rdf_type in conn.post_cell.rdf_type:
                    post_name = format_muscle_name(post_name)

                if not synclass:
                    # 缺少 synclass 时依其他字段猜测，保证生成模型时有有效的 synclass
                    # 临时方案：synclass 未知时按电突触和 DD/VD 前缀规则粗略猜测
                    if syntype and syntype.lower() == "gapjunction":
                        synclass = "Generic_GJ"
                    else:
                        if pre_name.startswith("DD") or pre_name.startswith("VD"):
                            synclass = "GABA"
                        synclass = "Acetylcholine"
                conns.append(
                    ConnectionInfo(pre_name, post_name, num, syntype, synclass)
                )

                pre_cell_names.add(pre_name)
                post_cell_names.add(post_name)

        print_(
            "Total cells %i (%i with connections)"
            % (
                len(self.cell_names | pre_cell_names | post_cell_names),
                len(pre_cell_names | post_cell_names),
            )
        )
        print_("Total connections found %i " % len(conns))

        return list(self.cell_names), pre_cell_names, post_cell_names, conns


def format_muscle_name(muscle_name):
    """将 owmeta 返回的肌肉名称转换为 c302 标准命名格式。

    :param muscle_name: owmeta 返回的原始肌肉名称
    :return: c302 标准格式的肌肉名称；无法解析时返回原名
    """
    md = MUSCLE_RE.fullmatch(muscle_name)
    if md:
        return muscle_name
    else:
        md = re.fullmatch(r"([VD][LR])(\d+)", muscle_name)
        if md:
            return "M{0}{1:02d}".format(md.group(1), int(md.group(2)))
        else:
            LOGGER.debug("Unrecognized muscle name format in %s", muscle_name)
            return muscle_name


# 模块级单例实例，使其接口与其他数据读取器一致（直接调用模块级函数）
READER = OpenWormReader()
# 为和其他读取器保持相同接口而创建模块级别名
read_data = READER.read_data
read_muscle_data = READER.read_muscle_data

if __name__ == "__main__":
    cells, neuron_conns = read_data(include_nonconnected_cells=True)
    neurons2muscles, muscles, muscle_conns = read_muscle_data()

    analyse_connections(cells, neuron_conns, neurons2muscles, muscles, muscle_conns)

    exit()

    conn_map_OWR = {}
    for c in neuron_conns:
        conn_map_OWR[c.short().lower()] = c

    from c302.UpdatedSpreadsheetDataReader import read_data as read_data_usr

    # [备选] 可替换为旧版 SpreadsheetDataReader 进行对比验证
    # from c302.SpreadsheetDataReader import read_data as read_data_usr

    cells2, conns2 = read_data_usr(include_nonconnected_cells=True)

    print_(
        "%i cells found using UpdatedSpreadsheetDataReader2: %s..."
        % (len(cells2), sorted(cells2)[0:3])
    )
    print_(
        "Found %s connections using UpdatedSpreadsheetDataReader2, First few: "
        % (len(conns2),)
    )
    for c in sorted(conns2)[: min(len(conns2), 5)]:
        print_("  %s" % c)

    conn_map_USR = {}
    for c2 in conns2:
        conn_map_USR[c2.short().lower()] = c2

    maxn = 3

    refs_OWR = list(conn_map_OWR.keys())

    matching = 0

    for i in range(min(maxn, len(refs_OWR))):
        ref = refs_OWR[i]
        if ref in conn_map_USR:
            if conn_map_OWR[ref].number != conn_map_USR[ref].number:
                print_("Mismatch: %s != %s" % (conn_map_OWR[ref], conn_map_USR[ref]))
            else:
                matching += 1
        else:
            print_(
                "Missing from UpdatedSpreadsheetDataReader: %s" % (conn_map_OWR[ref])
            )

    print_("Number matching: %i" % matching)

    matching = 0

    refs_USR = list(conn_map_USR.keys())

    for i in range(min(maxn, len(refs_USR))):
        # [调试] 可取消注释以打印 USR 连接详情
        # print("\n-----  Connection in USR: %s"%refs[i])
        # print cm2[refs[i]]
        ref = refs_USR[i]
        if ref in conn_map_OWR:
            if conn_map_OWR[ref].number != conn_map_USR[ref].number:
                print_("Mismatch: %s != %s" % (conn_map_OWR[ref], conn_map_USR[ref]))
            else:
                matching += 1
        else:
            print_("* Missing from OpenWormReader: %s" % conn_map_USR[ref])

    print_("Number matching: %i" % matching)
