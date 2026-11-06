from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model

from django.utils import timezone
from graphql_jwt.exceptions import JSONWebTokenExpired
from graphql_jwt.refresh_token.utils import get_refresh_token_model
from graphql_jwt.settings import jwt_settings

from .testCases import RelayTestCase, DefaultTestCase
from graphql_auth.constants import Messages


class RefreshTokenTestCaseMixin:
    def setUp(self):
        self.user = self.register_user(
            email="foo@email.com", username="foo", verified=True, archived=False
        )

    def test_refresh_token(self):
        query = self.get_login_query()
        executed = self.make_request(query)
        self.assertTrue(executed["refreshToken"])

        query = self.get_verify_query(executed["refreshToken"])
        executed = self.make_request(query)
        self.assertTrue(executed["success"])
        self.assertTrue(executed["refreshToken"])
        self.assertTrue(executed["payload"])
        self.assertFalse(executed["errors"])

    def test_invalid_token(self):
        query = self.get_verify_query("invalid_token")
        executed = self.make_request(query)
        self.assertFalse(executed["success"])
        self.assertFalse(executed["refreshToken"])
        self.assertFalse(executed["payload"])
        self.assertTrue(executed["errors"])

    def test_expired_token(self):
        # graphql_jwt raises JSONWebTokenExpired only when it decodes an expired
        # JWT, which the long running refresh token flow these settings use never
        # does, so the error is raised where that flow looks the token up.
        with mock.patch(
            "graphql_jwt.refresh_token.mixins.get_refresh_token",
            mock.MagicMock(side_effect=JSONWebTokenExpired),
        ):
            query = self.get_verify_query("expired_token")
            executed = self.make_request(query)
        self.assertFalse(executed["success"])
        self.assertEqual(executed["errors"]["nonFieldErrors"], Messages.EXPIRED_TOKEN)
        self.assertFalse(executed["refreshToken"])
        self.assertFalse(executed["payload"])

    def test_refresh_token_past_refresh_expiration_delta(self):
        # A long running refresh token older than JWT_REFRESH_EXPIRATION_DELTA
        # makes graphql_jwt raise a plain JSONWebTokenError, so it reads as invalid.
        query = self.get_login_query()
        refresh_token = self.make_request(query)["refreshToken"]
        max_age = jwt_settings.JWT_REFRESH_EXPIRATION_DELTA + timedelta(minutes=1)
        get_refresh_token_model().objects.filter(token=refresh_token).update(
            created=timezone.now() - max_age
        )

        query = self.get_verify_query(refresh_token)
        executed = self.make_request(query)
        self.assertFalse(executed["success"])
        self.assertEqual(executed["errors"]["nonFieldErrors"], Messages.INVALID_TOKEN)
        self.assertFalse(executed["refreshToken"])
        self.assertFalse(executed["payload"])


class RefreshTokenTestCase(RefreshTokenTestCaseMixin, DefaultTestCase):
    def get_login_query(self):
        return """
        mutation {
        tokenAuth(email: "foo@email.com", password: "%s" )
            { refreshToken, success, errors  }
        }
        """ % (
            self.default_password
        )

    def get_verify_query(self, token):
        return """
        mutation {
        refreshToken(refreshToken: "%s" )
            { success, errors, refreshToken, payload  }
        }
        """ % (
            token
        )


class RefreshTokenRelayTestCase(RefreshTokenTestCaseMixin, RelayTestCase):
    def get_login_query(self):
        return """
        mutation {
        tokenAuth(input:{ email: "foo@email.com", password: "%s"  })
            { refreshToken, success, errors  }
        }
        """ % (
            self.default_password
        )

    def get_verify_query(self, token):
        return """
        mutation {
        refreshToken(input: {refreshToken: "%s"} )
            { success, errors, refreshToken, payload  }
        }
        """ % (
            token
        )
