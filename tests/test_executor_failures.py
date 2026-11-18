import unittest
from unittest.mock import patch

from engine.executor import ExecutionEngine, MultiAgentExecutionError


class FailingRoleClient:
    def generate_content_sync(self, prompt, enable_search=False):
        if "请针对研究标的" in prompt:
            return "baseline"
        if "角色1" in prompt:
            raise RuntimeError("provider unavailable")
        return "role report"


class ErrorStringRoleClient:
    def generate_content_sync(self, prompt, enable_search=False):
        if "请针对研究标的" in prompt:
            return "baseline"
        if "角色1" in prompt:
            return "❌ Gemini API 响应异常 (HTTP 503)"
        return "role report"


class RecoveringSynthesisClient:
    def __init__(self):
        self.calls = 0

    def generate_content_sync(self, prompt, enable_search=False):
        self.calls += 1
        if self.calls == 1:
            return "❌ Gemini API 频次达到上限"
        return "final report"


class ExecutorFailureTests(unittest.TestCase):
    def test_role_failure_aborts_synthesis(self):
        engine = ExecutionEngine(FailingRoleClient())
        grounding = {
            "summary_badge": "test",
            "grounding_text": "",
            "gemini_search_allowed": False,
            "search_triggered": False,
        }

        with patch("engine.executor.data_hub.get_financial_grounding", return_value=grounding), \
                patch("engine.executor.time.sleep"), \
                patch.object(engine, "synthesize_memo") as synthesize, \
                self.assertRaises(MultiAgentExecutionError) as error:
            engine.execute_multi_agent_team("Example Corp")

        self.assertIn("段永平商业模式", str(error.exception))
        self.assertIn("provider unavailable", str(error.exception))
        synthesize.assert_not_called()

    def test_role_error_response_aborts_synthesis(self):
        engine = ExecutionEngine(ErrorStringRoleClient())
        grounding = {
            "summary_badge": "test",
            "grounding_text": "",
            "gemini_search_allowed": False,
            "search_triggered": False,
        }

        with patch("engine.executor.data_hub.get_financial_grounding", return_value=grounding), \
                patch("engine.executor.time.sleep"), \
                patch.object(engine, "synthesize_memo") as synthesize, \
                self.assertRaises(MultiAgentExecutionError) as error:
            engine.execute_multi_agent_team("Example Corp")

        self.assertIn("Gemini API 响应异常", str(error.exception))
        synthesize.assert_not_called()

    def test_synthesis_retries_and_accepts_recovery(self):
        client = RecoveringSynthesisClient()
        engine = ExecutionEngine(client)

        with patch("engine.executor.time.sleep"), patch.object(engine, "_save_report"):
            result = engine.synthesize_memo("Example Corp", {})

        self.assertEqual(result, "final report")
        self.assertEqual(client.calls, 2)


if __name__ == "__main__":
    unittest.main()
