from django.core.validators import MinValueValidator


class MinDateValueValidator(MinValueValidator):
    message = 'Ensure this value is greater than or equal to today\'s date.'
    code = 'min_value'

    def compare(self, a, b):
        return a < b
