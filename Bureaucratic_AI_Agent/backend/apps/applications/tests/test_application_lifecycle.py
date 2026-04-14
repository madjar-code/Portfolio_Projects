"""
Integration tests for the full application lifecycle:
  DRAFT → SUBMITTED → PROCESSING → APPROVED / REJECTED / FAILED

Mocked boundaries:
  - _publish_to_agent  — avoids real RabbitMQ connection in Celery task
  - publish_sse_event  — avoids real Redis connection in callback view
  File storage uses Django's InMemoryStorage (no MinIO needed).
"""
import hashlib
import hmac
import io
import json
import time
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.applications.constants import ApplicationStatus
from apps.applications.models import AIReport, Application

User = get_user_model()

_TEST_API_KEY = "test-secret-agent-key"

_STORAGE_OVERRIDE = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sign(body: bytes) -> dict:
    """Return X-Timestamp / X-Signature headers for a callback body."""
    ts = str(int(time.time()))
    message = f"{ts}.".encode() + body
    sig = hmac.new(_TEST_API_KEY.encode(), message, hashlib.sha256).hexdigest()
    return {"HTTP_X_TIMESTAMP": ts, "HTTP_X_SIGNATURE": sig}


def _callback_body(application_id, decision="ACCEPT", issues=None, recommendations=None) -> bytes:
    return json.dumps({
        "application_id": str(application_id),
        "decision": decision,
        "confidence_score": 0.95 if decision == "ACCEPT" else 0.2,
        "extracted_data": {"first_name": "Ion", "last_name": "Popescu"},
        "issues_found": issues or [],
        "recommendations": recommendations,
        "processing_time_seconds": 12,
        "ai_model_used": "gpt-4o-mini",
        "prompt_version": "v1",
    }).encode()


# ---------------------------------------------------------------------------
# Base test case
# ---------------------------------------------------------------------------

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    AGENT_API_KEY=_TEST_API_KEY,
    STORAGES=_STORAGE_OVERRIDE,
)
class ApplicationLifecycleTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="applicant@example.com",
            full_name="Ion Popescu",
            password="testpass123",
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _create_application(self) -> Application:
        fake_file = io.BytesIO(b"\xff\xd8\xff" + b"x" * 15_000)  # minimal JPEG-like bytes
        fake_file.name = "passport.jpg"
        with patch("apps.applications.tasks.process_application._publish_to_agent"):
            resp = self.client.post(
                reverse("application-create"),
                data={
                    "procedure": "passport_md",
                    "form_data": json.dumps({"first_name": "Ion", "last_name": "Popescu"}),
                    "document": fake_file,
                },
                format="multipart",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        return Application.objects.get(id=resp.data["id"])

    def _submit(self, app: Application) -> MagicMock:
        """Submit application. Returns the mock for _publish_to_agent."""
        with patch("apps.applications.tasks.process_application._publish_to_agent") as mock_pub:
            resp = self.client.post(
                reverse("application-submit", kwargs={"application_number": app.application_number}),
            )
        self.assertEqual(resp.status_code, 202, resp.data)
        app.refresh_from_db()
        return mock_pub

    def _send_callback(self, app: Application, **kwargs):
        body = _callback_body(app.id, **kwargs)
        headers = _sign(body)
        with patch("apps.applications.api.callback.publish_sse_event") as mock_sse:
            resp = self.client.post(
                reverse("agent-callback"),
                data=body,
                content_type="application/json",
                **headers,
            )
        return resp, mock_sse

    # -----------------------------------------------------------------------
    # Full lifecycle tests
    # -----------------------------------------------------------------------

    def test_lifecycle_accept(self):
        """DRAFT → SUBMITTED → PROCESSING → APPROVED"""
        app = self._create_application()
        self.assertEqual(app.status, ApplicationStatus.DRAFT)

        mock_pub = self._submit(app)
        self.assertEqual(app.status, ApplicationStatus.PROCESSING)
        mock_pub.assert_called_once()
        published_payload = mock_pub.call_args[0][0]
        self.assertEqual(published_payload["procedure"], "passport_md")
        self.assertEqual(published_payload["form_data"], {"first_name": "Ion", "last_name": "Popescu"})

        resp, mock_sse = self._send_callback(app, decision="ACCEPT")
        self.assertEqual(resp.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.APPROVED)

        report = AIReport.objects.get(application=app)
        self.assertEqual(report.decision, "ACCEPT")
        self.assertAlmostEqual(report.confidence_score, 0.95)
        self.assertEqual(report.ai_model_used, "gpt-4o-mini")
        self.assertEqual(report.prompt_version, "v1")

        mock_sse.assert_called_once_with(
            user_id=str(self.user.id),
            application_id=str(app.id),
            status=ApplicationStatus.APPROVED,
            application_number=app.application_number,
        )

    def test_lifecycle_reject(self):
        """DRAFT → SUBMITTED → PROCESSING → REJECTED with issues in report"""
        app = self._create_application()
        self._submit(app)

        issues = [{"field": "expiry_date", "detail": "Document expired on 26/05/2021", "severity": "critical"}]
        resp, mock_sse = self._send_callback(
            app,
            decision="REJECT",
            issues=issues,
            recommendations="Renew your passport before reapplying.",
        )
        self.assertEqual(resp.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.REJECTED)

        report = AIReport.objects.get(application=app)
        self.assertEqual(report.decision, "REJECT")
        self.assertEqual(report.issues_found, issues)
        self.assertEqual(report.recommendations, "Renew your passport before reapplying.")

        mock_sse.assert_called_once_with(
            user_id=str(self.user.id),
            application_id=str(app.id),
            status=ApplicationStatus.REJECTED,
            application_number=app.application_number,
        )

    def test_lifecycle_error(self):
        """PROCESSING → FAILED when agent returns ERROR decision"""
        app = self._create_application()
        self._submit(app)

        resp, mock_sse = self._send_callback(app, decision="ERROR")
        self.assertEqual(resp.status_code, 200)

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.FAILED)

        mock_sse.assert_called_once_with(
            user_id=str(self.user.id),
            application_id=str(app.id),
            status=ApplicationStatus.FAILED,
            application_number=app.application_number,
        )

    def test_report_upserted_on_second_callback(self):
        """A second callback for the same application updates the existing report."""
        app = self._create_application()
        self._submit(app)

        self._send_callback(app, decision="REJECT")
        self._send_callback(app, decision="ACCEPT")  # e.g. manual reprocessing

        app.refresh_from_db()
        self.assertEqual(app.status, ApplicationStatus.APPROVED)
        self.assertEqual(AIReport.objects.filter(application=app).count(), 1)
        self.assertEqual(AIReport.objects.get(application=app).decision, "ACCEPT")

    # -----------------------------------------------------------------------
    # Submit guard tests
    # -----------------------------------------------------------------------

    def test_cannot_submit_twice(self):
        """Submitting an already-submitted application returns 400."""
        app = self._create_application()
        self._submit(app)

        resp = self.client.post(
            reverse("application-submit", kwargs={"application_number": app.application_number}),
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("DRAFT", resp.data["error"]["message"])

    def test_submit_nonexistent_application_returns_404(self):
        resp = self.client.post(
            reverse("application-submit", kwargs={"application_number": "APP-00000000-XXXXX"}),
        )
        self.assertEqual(resp.status_code, 404)

    # -----------------------------------------------------------------------
    # Callback authentication tests
    # -----------------------------------------------------------------------

    def test_callback_invalid_signature_returns_401(self):
        app = self._create_application()
        body = _callback_body(app.id)
        resp = self.client.post(
            reverse("agent-callback"),
            data=body,
            content_type="application/json",
            HTTP_X_TIMESTAMP=str(int(time.time())),
            HTTP_X_SIGNATURE="invalidsignature",
        )
        self.assertEqual(resp.status_code, 401)

    def test_callback_missing_signature_returns_401(self):
        app = self._create_application()
        body = _callback_body(app.id)
        resp = self.client.post(
            reverse("agent-callback"),
            data=body,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_callback_replayed_request_returns_401(self):
        """Timestamp older than MAX_AGE_SECONDS must be rejected."""
        app = self._create_application()
        body = _callback_body(app.id)
        stale_ts = str(int(time.time()) - 120)  # 2 minutes ago
        message = f"{stale_ts}.".encode() + body
        sig = hmac.new(_TEST_API_KEY.encode(), message, hashlib.sha256).hexdigest()
        resp = self.client.post(
            reverse("agent-callback"),
            data=body,
            content_type="application/json",
            HTTP_X_TIMESTAMP=stale_ts,
            HTTP_X_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 401)

    def test_callback_unknown_application_returns_404(self):
        import uuid
        body = _callback_body(uuid.uuid4())
        headers = _sign(body)
        resp = self.client.post(
            reverse("agent-callback"),
            data=body,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 404)

    def test_callback_invalid_decision_returns_400(self):
        app = self._create_application()
        payload = json.dumps({
            "application_id": str(app.id),
            "decision": "MAYBE",
            "confidence_score": 0.5,
            "extracted_data": {},
            "issues_found": [],
            "processing_time_seconds": 1,
            "ai_model_used": "gpt-4o-mini",
        }).encode()
        headers = _sign(payload)
        resp = self.client.post(
            reverse("agent-callback"),
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 400)
