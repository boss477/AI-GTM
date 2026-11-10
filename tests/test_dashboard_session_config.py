import unittest

from dashboard.session_config import get_flask_session_secret


class FlaskSessionSecretTests(unittest.TestCase):
    def test_requires_configured_secret(self):
        with self.assertRaisesRegex(RuntimeError, "FLASK_SECRET_KEY"):
            get_flask_session_secret({})

    def test_rejects_blank_secret(self):
        with self.assertRaisesRegex(RuntimeError, "FLASK_SECRET_KEY"):
            get_flask_session_secret({"FLASK_SECRET_KEY": "   "})

    def test_uses_server_configured_secret(self):
        self.assertEqual(
            get_flask_session_secret({"FLASK_SECRET_KEY": "test-session-secret"}),
            "test-session-secret",
        )


if __name__ == "__main__":
    unittest.main()
