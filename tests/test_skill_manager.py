import unittest

from engine.skill_manager import skill_manager


class SkillManagerTests(unittest.TestCase):
    def test_build_prompt_includes_registered_skill_markdown(self):
        skill_id = next(
            skill_id
            for skill_id in skill_manager.registry
            if skill_id != "private-company-research"
        )
        raw_markdown = skill_manager.get_skill_raw_content(skill_id)

        prompt = skill_manager.build_prompt(skill_id, {"target": "Example Corp"})

        self.assertTrue(raw_markdown)
        self.assertIn(raw_markdown, prompt)
        self.assertNotIn("{raw_markdown}", prompt)

    def test_build_prompt_rejects_missing_skill_content(self):
        with self.assertRaises(FileNotFoundError):
            skill_manager.build_prompt("missing-skill", {})


if __name__ == "__main__":
    unittest.main()
