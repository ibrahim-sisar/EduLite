# users/tests/functions/test_prepare_dummy_data_config.py

from django.test import TestCase
from unittest.mock import patch, MagicMock

from ...management.logic import _prepare_dummy_data_config, get_choices_from_field

from ...models import UserProfile


class GetChoicesFromFieldTests(TestCase):
    """
    Test suite for the get_choices_from_field helper utility function.
    """

    def test_extracts_choices_correctly(self):
        """
        Test that the function correctly extracts the first value from each choice tuple.
        """
        # --- Setup Mock ---
        # Create a mock for a model field object
        mock_field = MagicMock()
        mock_field.choices = [
            ('DEV', 'Developer'),
            ('DSG', 'Designer'),
            ('', 'None'),          # This choice should be ignored because its value is empty
            ('PM', 'Project Manager')
        ]
        
        # Create a mock for a model class that will return our mock field
        mock_model = MagicMock()
        mock_model._meta.get_field.return_value = mock_field
        
        # --- Action ---
        result = get_choices_from_field(mock_model, 'any_field_name')
        
        # --- Assertions ---
        # Verify that get_field was called on the mock model's meta attribute
        mock_model._meta.get_field.assert_called_with('any_field_name')
        
        # Verify the result contains the correct values
        expected_choices = ['DEV', 'DSG', 'PM']
        self.assertEqual(result, expected_choices)

    def test_handles_field_without_choices_attribute(self):
        """
        Test that the function returns an empty list if the field has no 'choices' attribute.
        """
        # --- Setup Mock ---
        mock_field_no_choices = MagicMock()
        # To simulate the attribute not existing, we can use delattr
        # This requires the mock not to be a strict mock, which is the default for MagicMock
        if hasattr(mock_field_no_choices, 'choices'):
            del mock_field_no_choices.choices

        mock_model = MagicMock()
        mock_model._meta.get_field.return_value = mock_field_no_choices
        
        # --- Action ---
        result = get_choices_from_field(mock_model, 'any_field_name')
        
        # --- Assertions ---
        self.assertEqual(result, [])

    def test_handles_empty_choices_list(self):
        """
        Test that the function returns an empty list if the 'choices' attribute is empty.
        """
        # --- Setup Mock ---
        mock_field_empty_choices = MagicMock()
        mock_field_empty_choices.choices = []

        mock_model = MagicMock()
        mock_model._meta.get_field.return_value = mock_field_empty_choices
        
        # --- Action ---
        result = get_choices_from_field(mock_model, 'any_field_name')
        
        # --- Assertions ---
        self.assertEqual(result, [])


class PrepareDummyDataConfigTests(TestCase):
    """
    Test suite for the _prepare_dummy_data_config helper function.
    This now tests that it correctly uses the (mocked) get_choices_from_field utility.
    """

    # The path to patch is now the new location of the standalone utility function
    @patch('users.management.logic.get_choices_from_field')
    def test_fetches_model_choices_correctly(self, mock_get_choices_from_field):
        """
        Test that the function correctly calls the helper to get choices and populates the config.
        """
        # --- Setup Mock ---
        mock_countries = ['US', 'CA', 'MX']
        mock_occupations = ['Developer', 'Designer']
        mock_languages = ['en', 'es', 'fr']
        
        # Configure the mock to return different values based on which field is requested
        def get_choices_side_effect(model, field_name):
            if field_name == 'country':
                return mock_countries
            if field_name == 'occupation':
                return mock_occupations
            if field_name == 'preferred_language':
                return mock_languages
            return []
        
        mock_get_choices_from_field.side_effect = get_choices_side_effect

        # --- Action ---
        config = _prepare_dummy_data_config()

        # --- Assertions ---
        # 1. Check that the returned config dictionary has the correct values from our mocks
        self.assertEqual(config['country_options'], mock_countries)
        self.assertEqual(config['occupation_options'], mock_occupations)
        self.assertEqual(config['language_options'], mock_languages)

        # 2. Verify that the mocked helper function was called correctly
        self.assertEqual(mock_get_choices_from_field.call_count, 3)
        
        # Check that it was called with the correct arguments, order doesn't matter here
        mock_get_choices_from_field.assert_any_call(UserProfile, 'country')
        mock_get_choices_from_field.assert_any_call(UserProfile, 'occupation')
        mock_get_choices_from_field.assert_any_call(UserProfile, 'preferred_language')

    def test_returns_dictionary_with_expected_structure_and_paths(self):
        """
        Test that the function returns a dictionary with the correct keys
        and that the picture paths are correct.
        """
        # We can run this test without mocking to verify the static parts.
        config = _prepare_dummy_data_config()

        # 1. Test that the return value is a dictionary
        self.assertIsInstance(config, dict)

        # 2. Test that all expected keys are present
        expected_keys = [
            'country_options',
            'occupation_options',
            'language_options',
            'dummy_picture_paths'
        ]
        self.assertEqual(set(config.keys()), set(expected_keys))
    
        # 3. Test the hardcoded picture paths
        expected_paths = [
            'profile_pics/dummy/avatar1.png',
            'profile_pics/dummy/avatar2.png',
            'profile_pics/dummy/avatar3.png',
        ]
        self.assertEqual(config['dummy_picture_paths'], expected_paths)