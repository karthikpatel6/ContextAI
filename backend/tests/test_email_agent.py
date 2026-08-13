import asyncio
import importlib
import os
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class EmailAgentTests(TestCase):
    def test_run_agent_sends_email_for_simple_requests(self):
        original_cwd = os.getcwd()
        env_path = PROJECT_ROOT / ".env"
        self.assertTrue(env_path.exists(), "backend/.env file should exist for this test")

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                with patch.dict(
                    os.environ,
                    {"GROQ_API_KEY": "test", "TAVILY_API_KEY": "test", "EMAIL_ADDRESS": "", "EMAIL_PASSWORD": ""},
                    clear=True,
                ):
                    sys.modules.pop("agents.at_ai_agent", None)
                    agent_module = importlib.import_module("agents.at_ai_agent")

                    with patch("agents.at_ai_agent.send_email.func", return_value="Email sent successfully") as send_mock, patch(
                        "agents.at_ai_agent.agent.ainvoke",
                        side_effect=AssertionError("Llm graph should not be invoked for simple email dispatch"),
                    ):
                        result = asyncio.run(agent_module.run_agent("generate something and send email to user@example.com"))

                    self.assertIn("Email sent successfully", result)
                    send_mock.assert_called_once()
                    recipient, subject, body = send_mock.call_args.args
                    self.assertEqual(recipient, "user@example.com")
                    self.assertEqual(subject, "Generated content")
                    self.assertIn("ContextAI", body)
            finally:
                os.chdir(original_cwd)

    def test_send_email_loads_backend_env_file_when_cwd_is_elsewhere(self):
        original_cwd = os.getcwd()
        env_path = PROJECT_ROOT / ".env"
        self.assertTrue(env_path.exists(), "backend/.env file should exist for this test")

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                with patch.dict(
                    os.environ,
                    {"GROQ_API_KEY": "test", "TAVILY_API_KEY": "test", "EMAIL_ADDRESS": "", "EMAIL_PASSWORD": ""},
                    clear=True,
                ):
                    sys.modules.pop("agents.at_ai_agent", None)
                    agent_module = importlib.import_module("agents.at_ai_agent")

                    smtp_server = Mock()
                    smtp_server.__enter__ = Mock(return_value=smtp_server)
                    smtp_server.__exit__ = Mock(return_value=None)

                    expected_env = dotenv_values(env_path)
                    with patch("agents.at_ai_agent.smtplib.SMTP", return_value=smtp_server) as smtp_cls:
                        result = agent_module.send_email.func("user@example.com", "Subject", "Body")

                    self.assertIn("Email sent successfully", result)
                    smtp_cls.assert_called_once_with("smtp.gmail.com", 587)
                    smtp_server.starttls.assert_called_once_with()
                    smtp_server.login.assert_called_once_with(
                        expected_env.get("EMAIL_ADDRESS"),
                        expected_env.get("EMAIL_PASSWORD"),
                    )
            finally:
                os.chdir(original_cwd)
