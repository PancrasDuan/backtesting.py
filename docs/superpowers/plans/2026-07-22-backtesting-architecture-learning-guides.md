# Backtesting.py 架构学习文档实施计划

> **供执行代理使用：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，逐项实施本计划。所有步骤均使用复选框（`- [ ]`）跟踪状态。

**目标：** 基于源码基线 `cadcbe2`，生成一份完整的中文 Markdown 源码精读指南和一份自包含的交互式 HTML 学习地图。

**架构：** 两份产物共享一个由 `ARCHITECTURE_LEARNING_GOALS.md` 推导出的显式覆盖契约。Markdown 文档是带仓库源码链接和 Mermaid 图的深度教材；HTML 文档覆盖相同重点，但将其重组为支持键盘操作、阶段式探索和本地进度保存的交互学习体验。

**技术栈：** Markdown、Mermaid 语法、语义化 HTML5、CSS 自定义属性、原生 JavaScript、Python 3 标准库验证；环境可用时使用 Node.js 检查脚本语法，并通过浏览器完成渲染检查。

## 全局约束

- 所有说明和源码位置均绑定仓库基线 `cadcbe2`。
- 只在仓库根目录创建两份面向用户的正式产物：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md` 和 `BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html`。
- 两份产物都必须覆盖 `ARCHITECTURE_LEARNING_GOALS.md` 中的五项总目标、七个阅读阶段、四条调用链、架构不变量、系统边界、九项学习验收以及 Fork/上游同步建议。
- 不修改 `backtesting/` 下的运行代码、测试或公开 API。
- HTML 必须自包含、无服务端、无需联网、禁用 JavaScript 后仍可阅读、支持键盘操作，并在 320 px 宽度下正常重排。
- OHLC bar 内路径、成交、年化等模型化行为必须明确标注为“框架假设”或“模型限制”，不能描述成真实市场保证。
- 精确行为以源码和测试检查为准，不能只改写目标文件。

---

### 任务 1：建立可执行的内容覆盖契约

**文件：**

- 新建：`docs/superpowers/tests/test_learning_guides.py`
- 阅读：`ARCHITECTURE_LEARNING_GOALS.md`
- 阅读：`docs/superpowers/specs/2026-07-22-backtesting-architecture-learning-guide-design.md`

**接口：**

- 输入：目标文件和已确认的设计说明。
- 输出：两个 `unittest.TestCase` 测试类——`MarkdownGuideTests` 和 `HtmlGuideTests`，用于约束必备主题和文档结构。

- [ ] **步骤 1：先编写预期失败的验证测试**

创建一个只使用 Python 标准库的 `unittest` 模块，并写入以下完整契约：

```python
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
```

- [ ] **步骤 2：运行测试并确认处于 RED 状态**

运行：

```bash
python3 -m unittest docs/superpowers/tests/test_learning_guides.py -v
```

预期结果：两个测试类都在 `setUpClass` 阶段因 `FileNotFoundError` 失败，因为两份正式学习文档尚不存在。

- [ ] **步骤 3：提交可执行覆盖契约**

```bash
git add docs/superpowers/tests/test_learning_guides.py
git commit -m "test: define learning guide coverage"
```

### 任务 2：编写完整的 Markdown 源码精读指南

**文件：**

- 新建：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md`
- 测试：`docs/superpowers/tests/test_learning_guides.py`
- 阅读：`backtesting/__init__.py`
- 阅读：`backtesting/backtesting.py`
- 阅读：`backtesting/_util.py`
- 阅读：`backtesting/_stats.py`
- 阅读：`backtesting/_plotting.py`
- 阅读：`backtesting/lib.py`
- 阅读：`backtesting/test/_test.py`

**接口：**

- 输入：任务 1 中的 `REQUIRED_TOPICS`、`REQUIRED_PHASES`、`REQUIRED_CHAINS` 和 `REQUIRED_ACCEPTANCE` 内容契约。
- 输出：一份适合仓库内阅读的 Markdown 指南，包含稳定的相对源码链接、不少于八张 Mermaid 图、学习练习和完成清单。

- [ ] **步骤 1：确认 Markdown 专项测试因正确原因失败**

运行：

```bash
python3 -m unittest docs.superpowers.tests.test_learning_guides.MarkdownGuideTests -v
```

预期结果：因找不到 `BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md` 而出现 `FileNotFoundError`。

- [ ] **步骤 2：写作前核对精确源码行为**

使用 `rg` 和聚焦的 `sed` 范围检查以下机制：

```text
Strategy._check_params 与 Strategy.I
Backtest.__init__、Backtest.run、Backtest.optimize、Backtest._mp_task
_Data._set_length、_Data._update、_indicator_warmup_nbars
_Broker.new_order、next、_process_orders、_reduce_trade、_close_trade、_open_trade
compute_stats 与 compute_drawdown_duration_peaks
SharedMemoryManager、Pool、MultiBacktest
commission/spread/margin/trade_on_close/exclusive_orders/hedging/sl/tp/finalize_trades 相关测试
```

- [ ] **步骤 3：按已确认的知识架构编写 Markdown 指南**

采用以下固定的一级章节顺序：

```markdown
# Backtesting.py 源码架构学习指南
> 基线、定位与完成结果
## 如何使用这份指南
## 一张图建立系统全景
## 一次回测的完整旅程
## 阶段1：从公开 API 进入主循环
## 阶段2：时间推进与未来数据隔离
## 阶段3：订单、交易与持仓状态模型
## 阶段4：精读撮合引擎
## 阶段5：结果、统计与绘图
## 阶段6：参数优化与并行化
## 阶段7：把测试当作行为规格
## 四条调用链速查
## 交易生命周期推演
## 架构不变量与源码阅读记录模板
## 项目边界与迁移启示
## 学习完成验收
## Fork 与上游同步
## 附录：源码索引与术语表
```

文档必须包含模块边界、对象所有权、主循环时序、渐进数据窗口、订单状态、撮合决策、账户核算、统计溯源和多进程优化图。每个学习阶段都必须包含核心问题、阅读顺序、机制解释、常见误解、练习和检查项。只有在与基线 `cadcbe2` 核对后，才能加入精简的源码摘录。

- [ ] **步骤 4：运行 Markdown 验证并修复全部失败项**

运行：

```bash
python3 -m unittest docs.superpowers.tests.test_learning_guides.MarkdownGuideTests -v
git diff --check -- BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md
```

预期结果：3 个测试全部通过；`git diff --check` 以状态码 0 退出且不产生输出。

- [ ] **步骤 5：提交 Markdown 指南**

```bash
git add BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md
git commit -m "docs: add architecture learning guide"
```

### 任务 3：构建交互式 HTML 学习地图

**文件：**

- 新建：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html`
- 测试：`docs/superpowers/tests/test_learning_guides.py`
- 阅读：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md`

**接口：**

- 输入：Markdown 指南中已经核实的事实，以及任务 1 的共享测试常量。
- 输出：一个独立的 HTML 文档；所有核心内容都位于语义化 DOM 中，并由六类 `data-action` 交互增强。

- [ ] **步骤 1：确认 HTML 专项测试因正确原因失败**

运行：

```bash
python3 -m unittest docs.superpowers.tests.test_learning_guides.HtmlGuideTests -v
```

预期结果：因找不到 `BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html` 而出现 `FileNotFoundError`。

- [ ] **步骤 2：实现支持渐进增强的语义化标记**

创建一份完整的 HTML5 文档，结构必须包括：

```text
header：源码基线、学习目的、进度元素
nav：总览 + 阶段1..阶段7 + 调用链 + 交易推演 + 系统边界 + 学习验收
main：每个导航项对应一个 article 区段
buttons：data-action 值为 select-stage、toggle-detail、select-chain、
         step-order、toggle-answer、mark-complete
noscript：说明所有章节仍然可见，但不能保存学习进度
```

所有必备主题都必须存在于文本节点中，不能只放在 CSS 伪元素或脚本数据里。首次渲染默认显示总览；禁用 JavaScript 时，全部章节按文档顺序显示。

- [ ] **步骤 3：实现确定的交互状态模型**

使用一个状态对象和事件委托：

```javascript
const state = {
  stage: "overview",
  chain: "indicator",
  orderStep: 0,
  completed: new Set(loadProgress())
};

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem("backtesting-learning-progress") || "[]");
  } catch (error) {
    return [];
  }
}

function saveProgress() {
  try {
    localStorage.setItem("backtesting-learning-progress", JSON.stringify([...state.completed]));
  } catch (error) {
    // 即使无法持久化，正文阅读和当前会话内的进度仍可使用。
  }
}

function renderProgress() {
  const total = document.querySelectorAll("[data-completable]").length;
  const done = state.completed.size;
  const progress = document.getElementById("learning-progress");
  progress.max = total;
  progress.value = done;
  document.getElementById("learning-progress-label").textContent = `${done} / ${total}`;
}

function selectStage(stage) {
  state.stage = stage;
  document.querySelectorAll("[data-stage-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.stagePanel !== stage;
  });
  document.querySelectorAll('[data-action="select-stage"]').forEach((button) => {
    button.setAttribute("aria-current", button.dataset.stage === stage ? "page" : "false");
  });
}
```

为调用链切换和订单步骤切换增加对应的小型渲染函数。委托点击处理器必须分派全部六类 `data-action`，同步更新 ARIA 状态，并通过真实的 `button` 元素保留浏览器原生键盘行为。

- [ ] **步骤 4：实现响应式、主题自适应的视觉样式**

使用 CSS 自定义属性支持明暗主题；桌面端采用双栏布局，在 `@media (max-width: 640px)` 下重排为单栏；保留清晰的 `:focus-visible` 状态；不使用固定视口高度；实现 `prefers-reduced-motion`。图中颜色必须同时配合文字或形状传达含义。只有表格列确实无法容纳时，才使用横向滚动容器。

- [ ] **步骤 5：运行结构和语法验证**

运行：

```bash
python3 -m unittest docs.superpowers.tests.test_learning_guides.HtmlGuideTests -v
python3 -c 'from pathlib import Path; from html.parser import HTMLParser; p=HTMLParser(); p.feed(Path("BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html").read_text()); print("HTML parse: OK")'
```

将内联 JavaScript 提取到临时文件；若环境提供 Node.js，再对其运行 `node --check`。预期结果：3 个 HTML 测试全部通过、解析器输出 `HTML parse: OK`，并且 JavaScript 语法检查以状态码 0 退出。

- [ ] **步骤 6：在浏览器中渲染并逐项操作文档**

打开本地 HTML，在桌面和窄屏宽度下检查：

```text
阶段导航会切换当前显示的文章区段
详情和答案按钮会同步更新 aria-expanded 与内容可见性
四个调用链按钮会更新同一张关系图和说明
订单上一步/下一步会更新状态、标签和图形
标记完成会更新进度，刷新页面后仍能恢复
键盘焦点始终清晰可见
320 px 宽度下不存在文字重叠或裁切
```

- [ ] **步骤 7：提交 HTML 指南**

```bash
git add -f BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html
git commit -m "docs: add interactive architecture learning map"
```

### 任务 4：执行完整覆盖验证并交付

**文件：**

- 验证：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.md`
- 验证：`BACKTESTING_ARCHITECTURE_LEARNING_GUIDE.html`
- 验证：`docs/superpowers/tests/test_learning_guides.py`
- 验证：`ARCHITECTURE_LEARNING_GOALS.md`

**接口：**

- 输入：两份正式文档和可执行覆盖契约。
- 输出：最新验证证据，证明两份文档符合已确认设计，并且没有修改 Backtesting.py 的运行行为。

- [ ] **步骤 1：运行完整学习文档测试套件**

```bash
python3 -m unittest docs/superpowers/tests/test_learning_guides.py -v
```

预期结果：6 个测试全部通过，0 个失败，0 个错误。

- [ ] **步骤 2：运行仓库整洁性检查**

```bash
git diff --check
git status --short
```

预期结果：`git diff --check` 以状态码 0 退出。仓库状态只包含有意生成的学习文档相关变更，以及用户原先未跟踪的 `ARCHITECTURE_LEARNING_GOALS.md`。

- [ ] **步骤 3：人工执行目标到产物的逐项审计**

逐项阅读 `ARCHITECTURE_LEARNING_GOALS.md` 中的标题和检查项，为每一项记录对应的 Markdown 标题和 HTML 区段 ID。发现缺口时先修复，再进入完成状态。

- [ ] **步骤 4：交付两份正式产物**

在最终回复中链接仓库根目录的两份文件，简述各自不同的阅读体验，引用最新验证得出的测试数量和浏览器检查结果，并明确说明没有修改用户原先未跟踪的目标文件。
