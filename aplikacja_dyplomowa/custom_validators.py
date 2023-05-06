import re
from difflib import SequenceMatcher

from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    CommonPasswordValidator,
    UserAttributeSimilarityValidator,
    NumericPasswordValidator,
    exceeds_maximum_length_ratio
)
from django.core.exceptions import ValidationError
from django.core.exceptions import FieldDoesNotExist


class CustomMinimumLengthValidator(MinimumLengthValidator):

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Hasło powinno mieć conajmniej "
                    "%(min_length)d znaków.",
                    "Hasło powinno mieć conajmniej "
                    "%(min_length)d znaków.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_length)d character.",
            "Your password must contain at least %(min_length)d characters.",
            self.min_length,
        ) % {"min_length": self.min_length}


class CustomCommonPasswordValidator(CommonPasswordValidator):

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Hasło składa się ze byt popularnego słowa."),
                code="password_too_common",
            )

    def get_help_text(self):
        return _("Your password can’t be a commonly used password.")


class CustomNumericPasswordValidator(NumericPasswordValidator):

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Hasło nie może składać się z samych liczb."),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return _("Your password can’t be entirely numeric.")


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):

    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    try:
                        verbose_name = str(
                            user._meta.get_field(attribute_name).verbose_name
                        )
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("Hasło zbyt podobne do danych danych użytkownika."),
                        code="password_too_similar",
                        params={"verbose_name": verbose_name},
                    )

    def get_help_text(self):
        return _(
            "Your password can’t be too similar to your other personal information."
        )
