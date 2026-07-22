from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
MARKDOWN = ROOT / "BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md"
HTML = ROOT / "BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html"

REQUIRED_TOPICS = (
    "Backtest.run", "Strategy.I", "_Data", "_Indicator", "_Broker",
    "Position", "Order", "Trade", "_process_orders", "compute_stats",
    "_Stats", "SharedMemoryManager", "Pool", "MultiBacktest",
    "trade_on_close", "exclusive_orders", "hedging", "finalize_trades",
    "commission", "spread", "margin", "SL", "TP", "未来数据",
    "同 bar", "OHLC", "SAMBO", "Fork", "upstream",
)

REQUIRED_PHASES = tuple(f"阶段{i}" for i in range(1, 8))
REQUIRED_CHAINS = ("指标链", "下单与成交链", "平仓链", "结果链")
REQUIRED_ACCEPTANCE = (
    "10 分钟内画出", "逐行讲清", "默认市价单", "commission、spread、SL、TP",
    "未来数据泄漏", "同 bar 歧义", "主要指标的数据来源", "共享内存与多进程",
    "至少五项",
)


class GuideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.id_values = []
        self.data_actions = set()
        self.aria_controls = []
        self.stage_targets = set()
        self.stage_panels = set()
        self.stage_panel_ids = []
        self.chain_targets = set()
        self.chain_panels = set()
        self.order_markers = set()
        self.order_panels = set()
        self.completable_ids = set()
        self.complete_targets = []
        self.native_hidden = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
            self.id_values.append(attrs["id"])
        if "data-action" in attrs:
            self.data_actions.add(attrs["data-action"])
        if "aria-controls" in attrs:
            self.aria_controls.extend(attrs["aria-controls"].split())
        if "data-stage" in attrs:
            self.stage_targets.add(attrs["data-stage"])
        if "data-stage-panel" in attrs:
            self.stage_panels.add(attrs["data-stage-panel"])
            self.stage_panel_ids.append((attrs["data-stage-panel"], attrs.get("id")))
        if "data-chain" in attrs:
            self.chain_targets.add(attrs["data-chain"])
        if "data-chain-panel" in attrs:
            self.chain_panels.add(attrs["data-chain-panel"])
        if "data-order-marker" in attrs:
            self.order_markers.add(attrs["data-order-marker"])
        if "data-order-panel" in attrs:
            self.order_panels.add(attrs["data-order-panel"])
        if "data-completable" in attrs:
            self.completable_ids.add(attrs.get("id"))
        if attrs.get("data-action") == "mark-complete":
            self.complete_targets.append(
                attrs.get("data-complete-target") or attrs.get("data-target"))
        if "hidden" in attrs:
            self.native_hidden.append((tag, attrs.get("id")))

    def handle_data(self, data):
        self.text.append(data)


class MarkdownGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MARKDOWN.read_text(encoding="utf-8")

    def test_required_topics_are_covered(self):
        for term in REQUIRED_TOPICS + REQUIRED_PHASES + REQUIRED_CHAINS + REQUIRED_ACCEPTANCE:
            with self.subTest(term=term):
                self.assertIn(term, self.text)

    def test_visual_and_learning_structure_exists(self):
        self.assertGreaterEqual(self.text.count("```mermaid"), 8)
        self.assertGreaterEqual(self.text.count("- [ ]"), 20)
        self.assertIn("源码阅读记录模板", self.text)
        self.assertIn("交易生命周期推演", self.text)

    def test_clickable_toc_and_stage_dependencies_exist(self):
        self.assertIn("## 目录", self.text)
        self.assertIn("## 七阶段依赖地图", self.text)
        how_to = self.text.index("## 如何使用这份指南")
        toc = self.text.index("## 目录")
        dependencies = self.text.index("## 七阶段依赖地图")
        panorama = self.text.index("## 一张图建立系统全景")
        self.assertLess(how_to, toc)
        self.assertLess(toc, dependencies)
        self.assertLess(dependencies, panorama)

        expected_links = (
            "[系统全景](#一张图建立系统全景)",
            "[完整旅程](#一次回测的完整旅程)",
            "[阶段 1：公开 API](#阶段1从公开-api-进入主循环)",
            "[阶段 2：时间推进](#阶段2时间推进与未来数据隔离)",
            "[阶段 3：状态模型](#阶段3订单交易与持仓状态模型)",
            "[阶段 4：撮合引擎](#阶段4精读撮合引擎)",
            "[阶段 5：统计绘图](#阶段5结果统计与绘图)",
            "[阶段 6：优化并行](#阶段6参数优化与并行化)",
            "[阶段 7：测试规格](#阶段7把测试当作行为规格)",
            "[四条调用链](#四条调用链速查)",
            "[不变量与记录模板](#架构不变量与源码阅读记录模板)",
            "[项目边界](#项目边界与迁移启示)",
            "[学习验收](#学习完成验收)",
            "[Fork 与 upstream](#fork-与上游同步)",
        )
        for link in expected_links:
            with self.subTest(link=link):
                self.assertIn(link, self.text)

        dependency_section = self.text[dependencies:panorama]
        self.assertIn("```mermaid", dependency_section)
        self.assertIn("前置依赖", dependency_section)
        self.assertIn("可并行", dependency_section)
        self.assertIn("回看", dependency_section)
        for phase in REQUIRED_PHASES:
            with self.subTest(phase=phase):
                self.assertIn(phase, dependency_section)

    def test_repository_markdown_links_resolve(self):
        targets = re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)", self.text)
        local_targets = [target for target in targets if "://" not in target]
        for target in local_targets:
            with self.subTest(target=target):
                self.assertTrue((ROOT / target).exists(), target)


class HtmlGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = HTML.read_text(encoding="utf-8")
        cls.parser = GuideParser()
        cls.parser.feed(cls.source)
        cls.visible_text = " ".join(cls.parser.text)

    def test_required_topics_are_covered(self):
        for term in REQUIRED_TOPICS + REQUIRED_PHASES + REQUIRED_CHAINS + REQUIRED_ACCEPTANCE:
            with self.subTest(term=term):
                self.assertIn(term, self.visible_text)

    def test_interactive_controls_and_fallback_exist(self):
        self.assertTrue({"select-stage", "toggle-detail", "select-chain", "step-order", "toggle-answer", "mark-complete"}.issubset(self.parser.data_actions))
        self.assertIn("learning-progress", self.parser.ids)
        self.assertIn("localStorage", self.source)
        self.assertIn("try {", self.source)
        self.assertIn("noscript", self.source)

    def test_document_is_self_contained_and_semantic(self):
        self.assertNotIn("fetch(", self.source)
        self.assertNotRegex(self.source, r"<(?:script|link)[^>]+https?://")
        self.assertIn("<main", self.source)
        self.assertIn("<nav", self.source)
        self.assertIn("prefers-reduced-motion", self.source)
        self.assertIn("@media (max-width: 640px)", self.source)

    def test_ids_and_interactive_targets_are_consistent(self):
        duplicate_ids = sorted(
            value for value, count in Counter(self.parser.id_values).items()
            if count > 1
        )
        self.assertEqual(duplicate_ids, [])

        for target in self.parser.aria_controls:
            with self.subTest(attribute="aria-controls", target=target):
                self.assertIn(target, self.parser.ids)

        self.assertEqual(self.parser.stage_targets, self.parser.stage_panels)
        for stage, panel_id in self.parser.stage_panel_ids:
            with self.subTest(attribute="data-stage", target=stage):
                self.assertEqual(stage, panel_id)

        self.assertEqual(self.parser.chain_targets, self.parser.chain_panels)
        self.assertEqual(self.parser.order_markers, self.parser.order_panels)

        self.assertTrue(self.parser.complete_targets)
        for target in self.parser.complete_targets:
            with self.subTest(attribute="data-complete-target/data-target", target=target):
                self.assertIsNotNone(target)
                self.assertIn(target, self.parser.completable_ids)

        self.assertEqual(self.parser.native_hidden, [])


if __name__ == "__main__":
    unittest.main()
