# =============================================================================
# 功能描述：
#   c302.utils.helpers 模块的单元测试，覆盖路径管理、格式化、
#   正则匹配和颜色生成等全部公开函数。
#
# 类与方法索引：
#   TestGetProjectRoot               (L20)   — get_project_root() 测试
#     test_returns_path_with_pyproject (L22)  — 正向：返回包含 pyproject.toml 的路径
#   TestGetDataDir                   (L29)   — get_data_dir() 测试
#     test_returns_data_subdir       (L31)   — 正向：返回 data/ 子目录
#   TestGetMorphologyDir             (L38)   — get_morphology_dir() 测试
#     test_returns_morphology_subdir (L40)   — 正向：返回 data/morphology/
#   TestGetXmlDir                    (L47)   — get_xml_dir() 测试
#     test_returns_xml_subdir        (L49)   — 正向：返回 data/xml/
#   TestGetConnectomeDir             (L56)   — get_connectome_dir() 测试
#     test_returns_connectome_subdir (L58)   — 正向：返回 data/connectome/
#   TestGetParametersDir             (L65)   — get_parameters_dir() 测试
#     test_returns_parameters_subdir (L67)   — 正向：返回 data/parameters/
#   TestGetStrFromExponential        (L74)   — get_str_from_exponential() 测试
#     test_format_scientific         (L76)   — 正向：科学计数法格式化
#     test_format_integer            (L81)   — 正向：整数格式化
#     test_format_zero               (L86)   — 边界：零值格式化
#   TestGetRandomColourHex           (L92)   — get_random_colour_hex() 测试
#     test_format_pattern            (L94)   — 正向：返回 #RRGGBB 格式
#     test_unique_colors             (L100)  — 正向：多次调用不总是相同
#   TestIsRegexString                (L107)  — is_regex_string() 测试
#     test_regex_pattern             (L109)  — 正向：含 ^ 和 $ 返回 True
#     test_plain_string              (L113)  — 反向：普通字符串返回 False
#     test_partial_regex             (L117)  — 边界：仅含 ^ 返回 False
#   TestRegexMatch                   (L122)  — regex_match() 测试
#     test_match_success             (L124)  — 正向：正则匹配成功
#     test_match_failure             (L129)  — 反向：正则不匹配返回 None
#     test_non_regex_returns_none    (L134)  — 边界：非正则模式返回 None
#   TestElemInCollMatchesConn        (L139)  — elem_in_coll_matches_conn() 测试
#     test_match_found               (L141)  — 正向：集合中正则匹配成功
#     test_no_match                  (L146)  — 反向：集合中无匹配
#     test_empty_collection          (L151)  — 边界：空集合返回 False
#
# 更新日志：
#   2026-04-17  yi  初始创建
#
# 当前维护者：yi
# =============================================================================
import re

from c302.utils.helpers import (
    elem_in_coll_matches_conn,
    get_connectome_dir,
    get_data_dir,
    get_morphology_dir,
    get_parameters_dir,
    get_project_root,
    get_random_colour_hex,
    get_str_from_exponential,
    get_xml_dir,
    is_regex_string,
    regex_match,
)


class TestGetProjectRoot:
    """get_project_root() 测试。"""

    def test_returns_path_with_pyproject(self):
        """正向：返回的路径下应存在 pyproject.toml。"""
        root = get_project_root()
        assert (root / "pyproject.toml").exists()


class TestGetDataDir:
    """get_data_dir() 测试。"""

    def test_returns_data_subdir(self):
        """正向：返回 data/ 子目录且目录存在。"""
        data = get_data_dir()
        assert data.name == "data"
        assert data.exists()


class TestGetMorphologyDir:
    """get_morphology_dir() 测试。"""

    def test_returns_morphology_subdir(self):
        """正向：返回 data/morphology/ 且目录存在。"""
        morph = get_morphology_dir()
        assert morph.name == "morphology"
        assert morph.exists()


class TestGetXmlDir:
    """get_xml_dir() 测试。"""

    def test_returns_xml_subdir(self):
        """正向：返回 data/xml/ 且目录存在。"""
        xml = get_xml_dir()
        assert xml.name == "xml"
        assert xml.exists()


class TestGetConnectomeDir:
    """get_connectome_dir() 测试。"""

    def test_returns_connectome_subdir(self):
        """正向：返回 data/connectome/ 且目录存在。"""
        conn = get_connectome_dir()
        assert conn.name == "connectome"
        assert conn.exists()


class TestGetParametersDir:
    """get_parameters_dir() 测试。"""

    def test_returns_parameters_subdir(self):
        """正向：返回 data/parameters/ 且目录存在。"""
        params = get_parameters_dir()
        assert params.name == "parameters"
        assert params.exists()


class TestGetStrFromExponential:
    """get_str_from_exponential() 测试。"""

    def test_format_scientific(self):
        """正向：科学计数法数字应被格式化为 15 位小数。"""
        result = get_str_from_exponential(1e-05)
        assert result == "0.000010000000000"

    def test_format_integer(self):
        """正向：整数应被格式化为 15 位小数。"""
        result = get_str_from_exponential(3)
        assert result == "3.000000000000000"

    def test_format_zero(self):
        """边界：零应被格式化为全零。"""
        result = get_str_from_exponential(0)
        assert result == "0.000000000000000"


class TestGetRandomColourHex:
    """get_random_colour_hex() 测试。"""

    def test_format_pattern(self):
        """正向：返回值应匹配 #RRGGBB 格式。"""
        colour = get_random_colour_hex()
        assert re.match(r"^#[0-9a-f]{6}$", colour)

    def test_unique_colors(self):
        """正向：100 次调用应至少产生 2 种不同颜色。"""
        colors = {get_random_colour_hex() for _ in range(100)}
        # 随机生成 100 次几乎不可能全部相同
        assert len(colors) > 1


class TestIsRegexString:
    """is_regex_string() 测试。"""

    def test_regex_pattern(self):
        """正向：含 ^ 和 $ 的字符串应返回 True。"""
        assert is_regex_string("^ADAL$") is True

    def test_plain_string(self):
        """反向：普通字符串应返回 False。"""
        assert is_regex_string("ADAL") is False

    def test_partial_regex(self):
        """边界：仅含 ^ 不含 $ 应返回 False。"""
        assert is_regex_string("^ADAL") is False


class TestRegexMatch:
    """regex_match() 测试。"""

    def test_match_success(self):
        """正向：正则匹配成功时返回 Match 对象。"""
        result = regex_match("^ADA[LR]$", "ADAL")
        assert result is not None

    def test_match_failure(self):
        """反向：正则不匹配时返回 None。"""
        result = regex_match("^ADA[LR]$", "AVAL")
        assert result is None

    def test_non_regex_returns_none(self):
        """边界：非正则模式应直接返回 None。"""
        result = regex_match("ADAL", "ADAL")
        assert result is None


class TestElemInCollMatchesConn:
    """elem_in_coll_matches_conn() 测试。"""

    def test_match_found(self):
        """正向：集合中有正则元素匹配时返回 True。"""
        coll = ["^ADA[LR]$", "^AVA[LR]$"]
        assert elem_in_coll_matches_conn(coll, "ADAL") is True

    def test_no_match(self):
        """反向：集合中无元素匹配时返回 False。"""
        coll = ["^ADA[LR]$", "^AVA[LR]$"]
        assert elem_in_coll_matches_conn(coll, "RIML") is False

    def test_empty_collection(self):
        """边界：空集合应返回 False。"""
        assert elem_in_coll_matches_conn([], "ADAL") is False
