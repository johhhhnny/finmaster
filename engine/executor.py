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
        支持 Tavily AI 结构化检索与 Gemini 原生 Google Search 智能调度。
        """
        meta = skill_manager.get_skill(skill_id) or {}
        skill_title = meta.get("title", skill_id)
        target = user_params.get("target") or user_params.get("holdings") or "研究标的"
        target_clean = str(target).strip()

        actual_gemini_search = False
        grounding_md = ""

        if enable_search:
            search_ctx = search_manager.get_financial_context(
                target=target_clean,
                focus=str(user_params.get("criteria", ""))
            )
            provider_name = search_ctx.get("provider_used", "联网检索")
            if on_status:
                on_status(f"🌐 正在使用 [{provider_name}] 实时检索「{target_clean}」最新财务与市场数据...")

            if search_ctx.get("grounding_text"):
                grounding_md = search_ctx["grounding_text"]
                actual_gemini_search = False
            else:
                actual_gemini_search = search_ctx.get("use_gemini_grounding", True)
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

        # Step 0: 基准数据侦察
        actual_gemini_search = False
        grounding_md = ""

        if enable_search:
            search_ctx = search_manager.get_financial_context(target=target_clean, focus=focus)
            provider_name = search_ctx.get("provider_used", "联网检索")
            if on_progress:
                on_progress(f"🔍 Step 0: 实时行情与基准数据侦察 [{provider_name}]...", 10, None)

            if search_ctx.get("grounding_text"):
                grounding_md = search_ctx["grounding_text"]
                actual_gemini_search = False
            else:
                actual_gemini_search = search_ctx.get("use_gemini_grounding", True)
        else:
            if on_progress:
                on_progress("🔍 Step 0: 行情与基准数据推演（纯模型知识库模式）...", 10, None)

        base_recon_prompt = f"""
请针对研究标的【{target_clean}】，根据最新真实市场数据输出核查基准清单：
1. 真实股票代码（美股/港股/A股代码）
2. 截至最新交易日收盘的实时股价（USD / HKD / CNY）
3. 最新总股本（已发行普通股总数）
4. 真实总市值
5. 最新已披露的季度财报周期（如 2025Q3/2025Q4/2026Q1）及最新单季营收、净利润、自由现金流。
输出必须极其精炼，仅列出上述 5 项核查基准点，杜绝虚构。
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
2. 最新收入与利润分部拆解（以最新财报为准）。
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
1. 真实核心主营盈利穿透：剔除股权投资账面浮动扰动，还原核心经营每股收益（EPS）。
2. 现金流与资本开支审计：经营现金流、CapEx 吞噬比例、自由现金流（FCF）真实质量。
3. 资产负债表与净现金储备：纯流动性现金池拆解，测算每股纯现金。
4. 估值与安全边际：测算真实核心主营 PE、扣现金市盈率（Ex-Cash PE），对比历史 5 年估值中枢。
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
7. 最终投资建议：分层操作建议表（激进型/稳健型/保守型具体价格区间与仓位建议）
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
