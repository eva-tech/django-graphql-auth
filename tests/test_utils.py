import graphene
from django.test import SimpleTestCase

from graphql_auth.utils import with_late_fields


class LateFieldsOutput(graphene.ObjectType):
    success = graphene.Boolean()


LateFieldsOutput._meta.fields["token"] = graphene.Field(graphene.String)
LateFieldsOutput._meta.fields["refresh_token"] = graphene.Field(graphene.String)


class WithLateFieldsTestCase(SimpleTestCase):
    def test_late_field_is_not_an_init_argument(self):
        with self.assertRaises(TypeError):
            LateFieldsOutput(success=False, token="")

    def test_sets_given_late_fields(self):
        output = with_late_fields(LateFieldsOutput(success=False), token="")
        self.assertIs(output.success, False)
        self.assertEqual(output.token, "")

    def test_late_fields_not_given_default_to_none(self):
        output = with_late_fields(LateFieldsOutput(success=False), token="")
        self.assertIsNone(output.refresh_token)

    def test_returns_the_same_output(self):
        output = LateFieldsOutput(success=True)
        self.assertIs(with_late_fields(output), output)
