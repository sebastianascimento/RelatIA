from django.test import TestCase
from unittest.mock import patch
from analyzer.ai_agents.agents import AgentFactory
from analyzer.ai_agents.tasks import TaskFactory


class AgentTest(TestCase):
    def test_agent_factory_creates_agents(self):
        """Test that AgentFactory creates all three types of agents."""
        with patch("analyzer.ai_agents.agents.Ollama"):
            factory = AgentFactory()

            structure_agent = factory.create_structure_analyzer()
            security_agent = factory.create_security_analyzer()
            quality_agent = factory.create_quality_analyzer()

            self.assertEqual(structure_agent.role, "Code Structure Analyzer")
            self.assertEqual(security_agent.role, "Security Analyzer")
            self.assertEqual(quality_agent.role, "Code Quality Analyzer")


class TaskTest(TestCase):
    def test_task_factory_creates_tasks(self):
        """Test that TaskFactory creates tasks for each agent type."""
        with patch("analyzer.ai_agents.agents.Ollama"):
            agent_factory = AgentFactory()
            structure_agent = agent_factory.create_structure_analyzer()
            security_agent = agent_factory.create_security_analyzer()
            quality_agent = agent_factory.create_quality_analyzer()

            task_factory = TaskFactory()
            test_code = "def test():\n    pass"

            structure_task = task_factory.create_structure_analysis_task(
                structure_agent, test_code
            )
            security_task = task_factory.create_security_analysis_task(
                security_agent, test_code
            )
            quality_task = task_factory.create_quality_analysis_task(
                quality_agent, test_code
            )

            self.assertEqual(structure_task.agent.role, "Code Structure Analyzer")
            self.assertEqual(security_task.agent.role, "Security Analyzer")
            self.assertEqual(quality_task.agent.role, "Code Quality Analyzer")

            self.assertIn(test_code, structure_task.description)
            self.assertIn(test_code, security_task.description)
            self.assertIn(test_code, quality_task.description)
