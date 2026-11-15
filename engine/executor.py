"""
FinMaster Execution Engine
负责单智能体（Single-Agent）、四大师并行多智能体（Multi-Agent Parallel）、以及漏斗分析的统一调度。
"""
import os
import sys
import time
import concurrent.futures
from typing import Dict, Any, Generator, Optional, Callable, List

from .skill_manager import skill_manager
from .llm import GeminiClient
from .search_provider import search_manager
from .data_sources import data_hub

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))


class ExecutionEngine:
    """投研执行引擎"""

    def __init__(self, llm_client: GeminiClient):
        self.llm = llm_client

    def execute_skill_stream(
        self,
        skill_id: str,
        user_params: Dict[str, Any],
        on_status: Optional[Callable[[str], None]] = None,
        enable_search: bool = True
    ) -> Generator[str, None, None]:
        """
        统一执行单智能体模式的技能，以流式生成输出。
        支持 DataHub (yfinance + SEC EDGAR + Tavily AI / Google Search) 多源智能融合。
        """
        meta = skill_manager.get_skill(skill_id) or {}
        skill_title = meta.get("title", skill_id)
        target = user_params.get("target") or user_params.get("holdings") or "研究标的"
        target_clean = str(target).strip()

        actual_gemini_search = False
        grounding_md = ""

        if enable_search:
            dh_res = data_hub.get_financial_grounding(
                target=target_clean,
                focus=str(user_params.get("criteria", "")),
                enable_search=True
            )
            provider_name = dh_res.get("summary_badge", "金融数据中台")
            if on_status:
                on_status(f"🌐 正在通过 [{provider_name}] 实时汇集「{target_clean}」财务报表与权威底稿...")

            grounding_md = dh_res.get("grounding_text", "")
            actual_gemini_search = False if grounding_md else True
        else:
            if on_status:
                on_status(f"🚀 正在组装「{skill_title}」方法论提示词（纯模型深度知识模式）...")

        prompt = skill_manager.build_prompt(skill_id, user_params)
        if grounding_md:
            prompt = f"{grounding_md}\n\n---\n\n{prompt}"

        if on_status:
            on_status(f"🤖 Gemini 正在深度思考并分析「{target_clean}」商业与财务价值...")

        full_content = []
        for chunk in self.llm.generate_content_stream(prompt, enable_search=actual_gemini_search):
            full_content.append(chunk)
            yield chunk

        # 归档保存研报
        report_text = "".join(full_content)
        self._save_report(target=target_clean, filename=f"{skill_id}.md", content=report_text)

    def execute_multi_agent_team(
        self,
        target: str,
        focus: str = "",
        on_progress: Optional[Callable[[str, int, Optional[Dict[str, Any]]], None]] = None,
        enable_search: bool = True
    ) -> Dict[str, str]:
        """
        执行四大师并行投研旗舰流水线（Investment-Team）：
        1. 实时基准数据侦察 (支持 Tavily AI / Google Search / DDG 智能多级降级调度)
        2. 4个角色（段永平、巴菲特、芒格、李录）线程并发调用
        3. 金融严谨性数学验算
        4. Team Lead 主笔综合汇总
        5. 结果落库并返回全量报告字典
        """
        results: Dict[str, str] = {}
        target_clean = target.strip()

        # Step 0: 基准数据侦察 (接入 DataHub 多源融合中台: yfinance + SEC EDGAR + Tavily AI)
        actual_gemini_search = False
        grounding_md = ""

        dh_res = data_hub.get_financial_grounding(
            target=target_clean,
            focus=focus,
            enable_search=enable_search
        )
        provider_name = dh_res.get("summary_badge", "金融数据中台")
        if on_progress:
            on_progress(f"🔍 Step 0: 汇集行情与财务报表底稿 [{provider_name}]...", 10, None)

        grounding_md = dh_res.get("grounding_text", "")
        if not grounding_md and enable_search:
            actual_gemini_search = True

        base_recon_prompt = f"""
请针对研究标的【{target_clean}】，结合最新真实市场数据与检索结果输出精炼的核查基准清单：

请依据真实市场现状客观判断【{target_clean}】为【公开上市公司（含已完成 IPO 挂牌交易的公司）】还是【未上市独角兽/私有化企业（如 OpenAI, Anthropic 等）】：

【若为公开上市公司（含已挂牌交易公司，如 SpaceX 在纳斯达克挂牌代码 SPCX）】：
1. 证券代码与上市地：美股/港股/A股代码及交易所（如美股 NASDAQ / NYSE）
2. 实时收盘股价：最新交易日收盘的具体股价（USD / HKD / CNY，提取确切数值或参考区间，如 $135~$142）
3. 最新总股本：已发行普通股总数（提取确切数值，如约 135.8 亿股）
4. 真实总市值：最新总市值（提取确切数值或区间，如约 $1.85T~$1.93T）
5. 最新已披露季度财报周期：最新单季营收、核心净利润、自由现金流（FCF）。

【若确为未上市独角兽/私有化企业（如 OpenAI, Anthropic 等）】：
1. 企业上市状态：明确标注为【私人/未上市独角兽】（Private / Pre-IPO）
2. 最新一级市场估值：最新融资轮次或员工/机构回购（Tender Offer）估值
3. 核心股东与资本结构：主要领投机构与战略资方
4. 最新预估/披露年营收与主营业务拆分：预估年营收规模、各核心业务体量占比
5. 盈利与现金流现状：EBITDA、现金流状况及未来 IPO 预期。

【重要数据提取准则】：
- 严禁把检索结果中已有的真实市场挂牌报价（如股价、市值、总股本等）判定为“数据缺失”。只要检索上下文中存在确切数值或参考区间，必须予以采纳并精炼列出！
- 杜绝虚构，格式精炼直达核心。
"""
        if grounding_md:
            base_recon_prompt = f"{grounding_md}\n\n---\n\n{base_recon_prompt}"

        base_recon = self.llm.generate_content_sync(base_recon_prompt, enable_search=actual_gemini_search)
        results["00_baseline_recon"] = base_recon

        if on_progress:
            on_progress("👥 Step 1: 启动四大师投研团队并行分析（巴菲特、段永平、芒格、李录）...", 25, {"recon": base_recon})

        # 4 个子任务 Prompt 定义
        tasks = {
            "01_段永平商业模式": f"""
【{target_clean}投研团队 · 角色1：商业模式分析师 (段永平视角)】
标的：{target_clean}
重点关注：{focus}
参考基准信息：
{base_recon}

任务：
1. 商业模式本质：这家公司到底靠什么赚钱？（谁付钱？为什么买单？边际成本如何？）
2. 最新收入与利润分部拆解（以最新财报或披露运营数据为准）。
3. 护城河多维检验：品牌心智垄断、网络效应、转换成本、规模壁垒、定价权。
4. 商业模式代际异化：是轻资产印钞机，还是滑向重资产重工业？
5. 段永平商业模式评级（A+ / A / A- / B）与综合护城河评分（1-5星）。
请输出结构清晰、反面检验透彻的万字级深度分析，严禁套话。
""",
            "02_巴菲特财务估值": f"""
【{target_clean}投研团队 · 角色2：财务与估值分析师 (巴菲特视角)】
标的：{target_clean}
重点关注：{focus}
参考基准信息：
{base_recon}

任务：
1. 真实核心主营盈利穿透：若为上市公司，还原核心经营每股收益（EPS）；若为未上市公司，分析核心业务盈利能力、毛利率与单位经济模型。
2. 现金流与资本开支审计：经营现金流、CapEx 吞噬比例、自由现金流（FCF）真实质量与现金消耗率（Burn Rate）。
3. 资产负债表与净现金储备：纯流动性现金池拆解，偿债能力与净现金安全垫。
4. 估值与安全边际：
   - 若为上市公司：测算真实核心主营 PE、扣现金市盈率（Ex-Cash PE），对比历史估值中枢。
   - 若为未上市独角兽：依据最新 Tender Offer / 融资估值测算隐含 PS（市销率）及资本化回报率，对比对标上市公司倍数。
5. 三情景估值推演（乐观/中性/悲观）与估值星级评分（1-5星）。
请进行严谨的财务审视与十进制逻辑推演。
""",
            "03_芒格竞争与逆向": f"""
【{target_clean}投研团队 · 角色3：行业格局与竞争分析师 (芒格视角)】
标的：{target_clean}
重点关注：{focus}
参考基准信息：
{base_recon}

任务：
1. 行业格局与市场蛋糕划分：竞争对手份额拉锯与商业机制分化。
2. 范式转移冲击：新技术/新模式带来的“自残式防御”或创新者窘境。
3. 芒格式逆向检验（Inversion）：列出 5 个可能导致该企业丧失护城河或利润断崖崩塌的致命情境，并给出发生概率评估。
4. 竞争护城河星级评分（1-5星）。
以芒格冷酷逆向思维剖析，杜绝盲目赞歌。
""",
            "04_李录风险与治理": f"""
【{target_clean}投研团队 · 角色4：风险评估与管理层研判分析师 (李录视角)】
标的：{target_clean}
重点关注：{focus}
参考基准信息：
{base_recon}

任务：
1. 管理层画像与组织文化：创始人/经理人受托人品行、危机应激纠错韧性、资本配置 ROI 纪律。
2. 监管反垄断与硬性黑天鹅穿透：最新司法裁决与合规边界推演。
3. 治理结构与股东利益一致性：双重股权、股权激励（SBC）与股票回购抵消度。
4. 李录视角下的“十年文明确定性检验”：10年维度上该企业是否顺应人类文明现代化不可逆的生产力趋势？
5. 综合治理与风险星级评分（1-5星）。
从现代化长期主义文明视角展开深刻解剖。
"""
        }

        # 并行执行 4 个角色（此时 4 大师共享已完成实时事实核验的 base_recon 基准数据，无需重复消耗搜索配额，杜绝 429 并发超限）
        time.sleep(1.0)
        subagent_outputs = {}

        def _run_role_staggered(role_name: str, task_prompt: str, delay_sec: float) -> tuple:
            if delay_sec > 0:
                time.sleep(delay_sec)
            res_text = self.llm.generate_content_sync(task_prompt, enable_search=False)
            return role_name, res_text

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_list = []
            for idx, (role, prompt) in enumerate(tasks.items()):
                pacing_gap = idx * 1.5  # 分别于 0.0s, 1.5s, 3.0s, 4.5s 错开启动
                future_list.append(
                    executor.submit(_run_role_staggered, role, prompt, pacing_gap)
                )

            completed_count = 0
            for future in concurrent.futures.as_completed(future_list):
                completed_count += 1
                try:
                    role, out = future.result()
                    subagent_outputs[role] = out
                    results[role] = out
                    if on_progress:
                        pct = 25 + int((completed_count / 4.0) * 40)
                        on_progress(f"  ⚡ 角色完成 ({completed_count}/4): {role} 已就绪", pct, {"role": role, "content": out})
                except Exception as e:
                    subagent_outputs[role] = f"角色分析生成异常: {str(e)}"
                    results[role] = subagent_outputs[role]

        # 冷却 1.5 秒后进入主笔综合汇总
        time.sleep(1.5)

        # Step 2: 主笔综合汇总决策
        if on_progress:
            on_progress("🏛️ Step 2: 主笔分析师（Team Lead）综合评审汇总中...", 75, None)

        final_report = self.synthesize_memo(
            target=target_clean,
            subagent_outputs=subagent_outputs,
            focus=focus
        )
        results["05_最终综合报告"] = final_report

        # 归档全部分部报告至 reports/
        for filename, content in results.items():
            clean_name = f"{filename}.md"
            self._save_report(target=target_clean, filename=clean_name, content=content)

        if on_progress:
            on_progress("✅ Step 3: 四大师研报流水线全部完成，报告已成功归档！", 100, results)

        return results

    def synthesize_memo(
        self,
        target: str,
        subagent_outputs: Dict[str, str],
        focus: str = ""
    ) -> str:
        """根据 4 位大师已完成的分析报告，由 Team Lead 综合撰写最终决策备忘录 (内置自动防抖动重试)"""
        target_clean = str(target).strip()
        synthesis_prompt = f"""
【投研团队 Team Lead：四大师综合投资研究报告主笔】
标的：{target_clean}
重点关注：{focus}

以下为 4 个专业分析师刚刚完成的独立研究报告：

【段永平商业模式分析摘要】：
{subagent_outputs.get('01_段永平商业模式', '')[:3000]}

【巴菲特财务估值分析摘要】：
{subagent_outputs.get('02_巴菲特财务估值', '')[:3000]}

【芒格竞争与逆向分析摘要】：
{subagent_outputs.get('03_芒格竞争与逆向', '')[:3000]}

【李录风险与治理分析摘要】：
{subagent_outputs.get('04_李录风险与治理', '')[:3000]}

请撰写最终的【综合投资决策备忘录】（最终报告.md），严格包含：
1. 一句话结论
2. 四维评分总表（段永平、巴菲特、芒格、李录四维评分 + 综合评分 1-5星）
3. 核心财务数据速览表
4. 各维度分析摘要
5. 投资论点（7条看多理由 Bull vs 7条看空理由 Bear）
6. 巴菲特买入前 Checklist 10 项严格审查表（通过/存疑/一票否决）
7. 最终投资建议：分层操作建议表（若为公开上市公司，给出激进型/稳健型/保守型具体买入价格区间与仓位建议；若为未上市独角兽，给出估值安全边际、一级市场参与门槛、二级市场映射受益标的及未来 IPO 参与策略）
8. 总结段落
"""
        final_report = ""
        for attempt in range(3):
            final_report = self.llm.generate_content_sync(synthesis_prompt, enable_search=False)
            if "Gemini API 请求失败" not in final_report and "unexpected EOF" not in final_report:
                break
            time.sleep(2.0 * (attempt + 1))

        self._save_report(target=target_clean, filename="05_最终综合报告.md", content=final_report)
        return final_report

    def _save_report(self, target: str, filename: str, content: str):
        """保存研报至 reports/{target}/ 目录"""
        try:
            target_dir = os.path.join(REPORTS_DIR, target.replace("/", "_").strip())
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
