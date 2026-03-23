from unittest.mock import patch

from django.test import TestCase, override_settings

from custom_mail.models import Mail
from custom_mail.utils import _send


class MailUtilsTests(TestCase):
    @override_settings(
        DEFAULT_FROM_EMAIL="noreply@example.com",
        DEBUG_EMAIL=False,
        EMAIL_HOST="localhost",
        EMAIL_PORT=25,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_USE_SSL=False,
        EMAIL_USE_TLS=False,
    )
    @patch("custom_mail.utils.render_to_string", return_value="rendered")
    @patch("custom_mail.utils.get_connection")
    def test_send_handles_invalid_json_without_eval(self, mock_get_connection, mock_render_to_string):
        mock_connection = mock_get_connection.return_value
        mail = Mail.objects.create(
            to_who="user@example.com",
            subject="Test",
            template_name="dummy",
            json_message="not valid json",
        )

        _send(mail)

        mail.refresh_from_db()
        self.assertTrue(mail.sent)
        self.assertEqual(mail.retry, 0)
        mock_connection.send_messages.assert_called_once()
