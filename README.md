# 🦅 FinMaster — 价值投资大师工作站

> **独立运行、开箱即用、覆盖 21 项顶级投资技能的多 Agent 价值投资操作系统**  
> 仅需一个 `GEMINI_API_KEY`，即可开启具备实时 Google Search 联网检索的顶级四大师投研流水线。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![UI: Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Model: Google Gemini](https://img.shields.io/badge/Model-Gemini%202.5%20%2F%20Flash-4285F4.svg)](https://ai.google.dev/)
[![Upstream: ai-berkshire](https://img.shields.io/badge/Upstream-ai--berkshire-green.svg)](https://github.com/xbtlin/ai-berkshire)

---

## 🔗 与开源项目 ai-berkshire 的渊源与演进关系

**FinMaster（价值投资大师工作站）** 诞生于对优秀开源价值投资研究项目 [**ai-berkshire**](https://github.com/xbtlin/ai-berkshire)（作者：[@xbtlin](https://github.com/xbtlin)）的深度衍生与二次研发。

### 1. 渊源与致敬
`ai-berkshire` 创新性地将**巴菲特、查理·芒格、段永平、李录**四位顶级投资大师的投资哲学与决策纪律进行了工程化提炼，开创了一套基于多智能体角色对抗、强制给明确买卖结论、严禁浮点误差与防本地数据污染的投研方法论。FinMaster 完整继承并吸收了 `ai-berkshire` 积淀的 **21 项专业投资技能 Prompt 资产** 与严谨的金融审计规则，向原作者的卓越贡献致以诚挚敬意。

### 2. 差异化定位演进
- **ai-berkshire**：定位为**面向极客与开发者的投研方法论底座与 CLI/Slash-Command 框架**，主要运行在 Claude Code、Codex 等特定终端环境。
- **FinMaster**：定位为**面向所有专业投资人、分析师与个人投资者的独立开箱即用图形化 Web 智能投研工作站**。它打破了终端与私有环境壁垒，重构了底层调度引擎与交互体验，让顶级的价值投资 AI 智囊团触手可及。

---

## ⚖️ 开源许可证合规评估（关于 ai-berkshire 对本项目开源的影响）

经详细法务审查，**`ai-berkshire` 的开源许可证对 `FinMaster` 在 GitHub 上独立开源完全没有任何限制与负面影响**，属于 **100% 许可兼容与合规**。

### 详细合规依据：
1. **上游许可证类型**：`ai-berkshire` 采用国际通用的标准 **MIT License**（Copyright (c) 2026 xbtlin）。
2. **MIT 许可核心权利**：
   - MIT 属于极其自由宽松的宽松型开源协议（Permissive License）。
   - 协议明确授予使用者在**无限制（without restriction）**的情况下使用、复制、修改、合并、发布、分发、再许可（sublicense）以及销售软件副本的权利。
   - **无传染性限制（Non-copyleft）**：与 GPL/AGPL 不同，MIT 许可不强制衍生作品采用特定架构或开源传染，也不禁止下游项目将其改造为独立产品发布。
3. **法定义务与履行方式**：
   - MIT 协议的唯一要求是：**在软件的所有副本或重要部分中保留原始版权声明和许可声明**（*"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."*）。
   - **FinMaster 的合规落实**：
     - 本项目同样采用 **MIT License** 开源。
     - 在本项目的 [`LICENSE`](LICENSE) 文件中已完整保留原作者的版权声明（`Portions Copyright (c) 2026 xbtlin`）。
     - 在本说明文档中清晰注明了 Prompt 资产及方法论的渊源，遵循开源社区最高的道德与版权规范。

---

## 💡 痛点解决与特性演进对比

FinMaster 针对 `ai-berkshire` 在实际日常使用过程中遇到的痛点与壁垒，进行了全方位的工程重构与功能创新：

| 维度 | 原项目 (ai-berkshire) 痛点 | FinMaster (价值投资大师工作站) 解决方案与优化 |
| :--- | :--- | :--- |
| **交互媒介** | 仅支持命令行终端或聊天框 Slash Command，交互生硬，普通投资人上手困难 | **现代化专业金融终端 Web UI**：纯浏览器操作，自适应宽屏排版，零代码门槛 |
| **运行环境** | 强绑定 Claude Code 或 Codex 商业客户端环境 | **独立开箱即用**：纯 Python + Streamlit 构建，任何 Mac / Windows / Linux 机器或 Docker 一键启动 |
| **API 成本与额度痛点** | 需配置昂贵的商业大模型，或受制于 Gemini 每日 20 次搜索硬限制 | **多级弹性联网架构**：内置 **Tavily AI（免费 1,000次/月独立配额）**、Gemini 原生 Google Search 与 DuckDuckGo 免Key 智能降级，**彻底告别 20 次限流与额外账单** |
| **并发与稳定性** | 多智能体并行发起请求时，极易因并发激增触发 API 429 限流崩溃 | **防 429 智能指数退避重试**：引擎底层实现带抖动的指数重试（Jittered Backoff）与弹性降级，确保长时间投研稳定不中断 |
| **执行透明度** | 终端运行过程中黑盒等待，看不到各智能体的分工执行进度与状态 | **四大师并行实时进度看板**：段永平、巴菲特、芒格、李录四角色卡片并行流式推进，各维度结论一目了然 |
| **研报资产管理** | 生成的报告散落于本地层级深厚的文件夹中，无检索与预览功能 | **交互式历史研报知识库**：自带全文检索、标的快捷筛选 Chips、Markdown 渲染阅览器与一键导出下载 |
| **估值计算工具** | 金融严谨性校验工具仅限 CLI 命令行手工输入长参数，缺乏直观反馈 | **交互式十进制高精度计算器**：可视化纯 `Decimal` 运算，提供美/港/A股预设芯片一键填参、巴菲特安全边际审计与三情景 CAGR 推演 |
| **代码工程架构** | 早期单脚本或混合脚本难以拆分二次开发 | **MVC 彻底解耦架构**：主控制器 `app.py` 仅 40 行，UI 视图层与后端引擎层清晰解耦，模块化极易二次开发与维护 |

---

## 🌟 FinMaster 核心新特性全览

### 1. 独立极简解耦架构 (MVC)
整个工作台严格遵循模块化工程规范设计：
- `finmaster/app.py`：仅保留 40 行极简应用控制器，负责路由调度；
- `finmaster/ui/`：独立视图模块，划分为 `styles.py`（金融终端全局样式规范）、`sidebar.py`（侧边栏与模型设置）、`workbench.py`（投研主工作台）、`archive.py`（研报知识库）和 `calculator.py`（十进制严谨性计算器）；
- `finmaster/engine/`：包含 LLM 统一通信、并发任务调度、21 项技能注册中心与持久化配置引擎。

### 2. 21 项专业投资技能全覆盖
无需记忆复杂的 Prompt，下拉菜单按投资全流程清晰分类：
- 🔍 **初筛与赛道漏斗**：行业漏斗筛选、去劣筛选（7条指标快速排除）、供应链瓶颈猎手、时代α捕手。
- 🏢 **深度个股研究**：**四大师投研团队（旗舰并行）**、财报精读团队、深度公司系列、管理层纵深研究、未上市公司研究等。
- ⚖️ **估值与投资准则**：巴菲特买入前 Checklist（10项严格审查）、收息投资评估、段永平问答（以他的方式思考）。
- ⏱️ **投后跟踪与风控**：公司新闻脉搏（异动快速归因）、投资论文追踪、投资论文漂移检测、组合管理体检。
- 📢 **成果转化与发布**：微信公众号文章一键转写排版。

### 3. 四大师视角对抗与实时流式看板
在核心技能「四大师投研团队」中，系统并行激活四位大师角色，形成互不妥协的张力：
- 🔴 **段永平**：聚焦商业模式、商业常识与「买股票就是买公司」的十年确定性；
- 🔵 **巴菲特**：聚焦自由现金流造血能力、资本分配记录与安全边际；
- 🟣 **查理·芒格**：逆向思维，全面推演技术颠覆、行业内卷与商业模式的毁灭情境；
- 🟢 **李录**：审视管理层的受托责任、品格、薪酬对齐度及时代文明周期。
前端页面通过优雅的多列卡片实时展示各角色的运行状态，产出结构化决策建议。

### 4. 交互式历史研报知识库 (Knowledge Base Archive)
- **快捷筛选 Chips**：一键筛选热门覆盖公司（谷歌、苹果、特斯拉、贵州茅台、腾讯等）；
- **全文即时过滤**：支持按研报文件名或内容关键字毫秒级检索；
- **沉浸式阅读与下载**：内嵌 Markdown 报告阅读器，并支持 `.md` 原稿一键下载。

### 5. 交互式纯十进制金融严谨性计算器 (Decimal Rigor Calculator)
为贯彻巴菲特价值投资的数学严谨性，内置可视化纯十进制高精度估值验算器：
- **基准标的一键填参**：支持一键载入 Alphabet、Apple、Tesla、茅台、腾讯等典型财报模型参数；
- **5 大核心指标卡片**：净利润、自由现金流 (FCF)、静态市盈率、扣现金市盈率 (Ex-Cash PE)、净资产收益率 (ROE)；
- **巴菲特安全边际审计卡片**：自动与内在价值比较，标记安全边际厚度与防亏损提示；
- **市值与股本匹配审计**：以 1% 极小容差验证当前股价与总股本推算的隐含市值是否一致；
- **未来收益三情景推演**：根据悲观（保守）、中性（基准）、乐观三组增速与退出市盈率，自动测算未来 5 年的复合年化收益率 (CAGR)。

---

## 🚀 快速启动指南

### 方式一：本地极速运行（推荐）

#### 1. 克隆项目并安装依赖
```bash
git clone https://github.com/your-username/finmaster.git
cd finmaster
pip install -r requirements.txt
```

#### 2. 配置 API Key（两种方式任选其一）
- **环境变量方式**：
  ```bash
  export GEMINI_API_KEY="你的_Google_Gemini_API_Key"
  ```
- **网页直接填写**：启动 Web 界面后，在左侧边栏的「系统与模型设置」中直接输入，系统会自动持久化保存。

#### 3. 启动 Web 工作台
```bash
streamlit run app.py
```
终端将输出访问链接，浏览器自动打开 `http://localhost:8501`。

---

### 方式二：Docker 容器化部署

FinMaster 提供了开箱即用的轻量级 Dockerfile：

```bash
# 构建镜像
docker build -t finmaster .

# 启动容器
docker run -d \
  -p 8501:8501 \
  -e GEMINI_API_KEY="你的_Google_Gemini_API_Key" \
  --name finmaster-workbench \
  finmaster
```
访问 `http://localhost:8501` 即可体验。

---

## 📁 项目目录结构

```text
finmaster/
├── app.py                  # Streamlit Web 主工作台（仅 40 行调度控制器）
├── start.py                # 一键快速启动检查脚本
├── requirements.txt        # 核心依赖清单 (streamlit, google-genai 等)
├── Dockerfile              # 容器化独立部署镜像配置
├── .env.example            # 环境变量配置模板
├── LICENSE                 # MIT 开源许可证（包含上游版权致敬）
├── README.md               # 项目使用说明书
├── ui/                     # 独立可视化界面层 (模块化解耦)
│   ├── styles.py           # 全局金融终端 CSS 样式、字体层级体系与 Streamlit 杂项隐蔽
│   ├── sidebar.py          # 侧边栏品牌、工作台导航、技能精选与模型设置
│   ├── workbench.py        # 智能投研工作台（Hero 看板、参数面板、标的 Chips、4大预检展台、实时卡片）
│   ├── archive.py          # 历史研报知识库（全文检索、公司过滤、Markdown 阅读与下载）
│   └── calculator.py       # 金融严谨性计算器（扣现金 PE 验算、市值股本校验、三情景 CAGR 推演）
├── engine/                 # 后端核心调度与服务引擎
│   ├── config.py           # 环境变量与配置持久化引擎
│   ├── llm.py              # Gemini 官方 SDK 与 Direct REST SSE 流式调用 (含防 429 重试与搜索降级)
│   ├── executor.py         # 单智能体与多智能体并行流水线调度器
│   ├── skill_manager.py    # 21 项技能注册与动态提示词装配
│   └── archive_manager.py  # 历史研报扫描、索引与全文检索
├── skills/                 # 21 个投资方法论核心 Prompt 资产 (.md)
├── tools/                  # 确定性金融与审计工具
│   ├── financial_rigor.py  # 高精度十进制估值与市值核验
│   └── report_audit.py     # 双源交叉数据抽检与准出审计
└── reports/                # 本地研报归档数据库（附带标杆样例研报）
```

---

## 🛡️ 研究质量与投资纪律准则

FinMaster 严格恪守价值投资基本原则：
1. **防本地历史数据污染（Anti-Local-Contamination）**：严禁读取本地历史陈旧数据推断当前市场。所有投资标的的最新现价、总市值与财报数据，必须通过联网检索或最新官方 10-Q/10-K 披露确认，并注明数据基准日。
2. **拒绝浮点误差与心算漂移（Absolute Decimal Rigor）**：所有估值乘数、自由现金流折现与复合年化收益率，均采用纯十进制高精度计算工具严格验算。
3. **强制给出明确买卖结论**：报告杜绝模棱两可的两面讨好式言论，必须依据安全边际分层给出激进型、稳健型与保守型投资者的明确建议及防亏损底线。

---

## 🤝 致谢与声明

- **致谢上游**：感谢开源项目 [ai-berkshire](https://github.com/xbtlin/ai-berkshire) 及其创作者 [@xbtlin](https://github.com/xbtlin) 建立的高水平价值投资工程化方法论框架。
- **免责声明**：本项目仅供计算机技术学习、投资哲学研究与个人辅助分析使用，不构成任何形式的投资建议、投资推介或买卖要约。市场有风险，投资需独立思考、谨慎决策。

---

*FinMaster — 价值投资大师工作站，让每位投资者拥有属于自己的 AI 价值投资智囊团。*
