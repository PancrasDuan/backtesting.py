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
        self.data_actions = set()
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if "data-action" in attrs:
            self.data_actions.add(attrs["data-action"])

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


if __name__ == "__main__":
    unittest.main()
