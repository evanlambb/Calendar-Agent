import pytest
from unittest.mock import patch, MagicMock
from tools import create_event

class TestCreateEvent:
    
    @patch('tools.build')
    @patch('tools.get_credentials')
    def test_create_event_basic_success(self, mock_creds, mock_build):
        """Test basic event creation with required parameters only"""
        # Mock the Google Calendar API
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute.return_value = {
            'htmlLink': 'https://calendar.google.com/event123'
        }
        
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00"
        )
        
        assert "✅ Event 'Test Meeting' created successfully!" in result
        assert "https://calendar.google.com/event123" in result
    
    @patch('tools.build')
    @patch('tools.get_credentials')
    def test_create_event_with_duration(self, mock_creds, mock_build):
        """Test event creation using duration instead of end_time"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute.return_value = {'htmlLink': 'test-link'}
        
        result = create_event(
            summary="Workout",
            start_time="2025-01-16 14:00",
            duration_minutes=60
        )
        
        assert "✅" in result
        # Verify the API was called with correct end time (14:00 + 60 min = 15:00)
        call_args = mock_service.events().insert.call_args[1]['body']
        assert "2025-01-16T15:00:00" in call_args['end']['dateTime']
    
    @patch('tools.build')
    @patch('tools.get_credentials')
    def test_create_event_with_all_options(self, mock_creds, mock_build):
        """Test event creation with all optional parameters"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute.return_value = {'htmlLink': 'test'}
        
        result = create_event(
            summary="Team Meeting",
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00",
            description="Weekly team sync",
            location="Conference Room A",
            attendees=["alice@example.com", "bob@example.com"]
        )
        
        assert "✅" in result
        
        # Verify all fields were included in API call
        call_args = mock_service.events().insert.call_args[1]['body']
        assert call_args['summary'] == "Team Meeting"
        assert call_args['description'] == "Weekly team sync"
        assert call_args['location'] == "Conference Room A"
        assert len(call_args['attendees']) == 2
        assert call_args['attendees'][0]['email'] == "alice@example.com"
    
    @patch('tools.build')
    @patch('tools.get_credentials')
    def test_create_recurring_event(self, mock_creds, mock_build):
        """Test creating recurring events"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events().insert().execute.return_value = {'htmlLink': 'test'}
        
        result = create_event(
            summary="Daily Standup",
            start_time="2025-01-16 09:00",
            duration_minutes=30,
            repeat_frequency="daily",
            repeat_count=5
        )
        
        assert "✅" in result
        
        # Verify recurrence was added
        call_args = mock_service.events().insert.call_args[1]['body']
        assert 'recurrence' in call_args
        assert "RRULE:FREQ=DAILY;COUNT=5" in call_args['recurrence'][0]

    # NEW/UPDATED: Required Parameter Validation Tests
    def test_empty_summary(self):
        """Test validation of empty summary"""
        result = create_event(
            summary="",  # Empty string
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Event summary cannot be empty" in result
    
    def test_whitespace_only_summary(self):
        """Test validation of whitespace-only summary"""
        result = create_event(
            summary="   ",  # Only whitespace
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Event summary cannot be empty" in result
    
    def test_none_summary(self):
        """Test validation of None summary"""
        result = create_event(
            summary=None,  # None value
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Event summary cannot be empty" in result
    
    def test_empty_start_time(self):
        """Test validation of empty start_time"""
        result = create_event(
            summary="Test Meeting",
            start_time="",  # Empty string
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Start time cannot be empty" in result
    
    def test_whitespace_only_start_time(self):
        """Test validation of whitespace-only start_time"""
        result = create_event(
            summary="Test Meeting",
            start_time="   ",  # Only whitespace
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Start time cannot be empty" in result
    
    def test_none_start_time(self):
        """Test validation of None start_time"""
        result = create_event(
            summary="Test Meeting",
            start_time=None,  # None value
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Start time cannot be empty" in result

    # Existing validation tests (unchanged)
    def test_missing_end_time_and_duration(self):
        """Test that either end_time or duration must be provided"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00"
        )
        assert "❌ Error: Please provide either end_time OR duration_minutes" in result
    
    def test_both_end_time_and_duration_provided(self):
        """Test that both end_time and duration cannot be provided"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            end_time="2025-01-16 15:00",
            duration_minutes=60
        )
        assert "❌ Error: Please provide either end_time OR duration_minutes, not both" in result
    
    def test_invalid_datetime_format(self):
        """Test datetime format validation"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025/01/16 2pm",  # Wrong format
            end_time="2025-01-16 15:00"
        )
        assert "❌ Error: Please use format 'YYYY-MM-DD HH:MM' for times" in result
    
    def test_invalid_repeat_frequency(self):
        """Test repeat frequency validation"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            duration_minutes=60,
            repeat_frequency="yearly",  # Not supported
            repeat_count=3
        )
        assert "❌ Error: repeat_frequency must be 'daily', 'weekly', or 'monthly'" in result
    
    def test_repeat_frequency_without_count(self):
        """Test that repeat_count is required when repeat_frequency is provided"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            duration_minutes=60,
            repeat_frequency="daily"
            # Missing repeat_count
        )
        assert "❌ Error: If repeat_frequency is provided, repeat_count is required" in result

    def test_repeat_count_without_frequency(self):
        """Test that repeat_frequency is required when repeat_count is provided"""
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            duration_minutes=60,
            repeat_count=5
            # Missing repeat_frequency
        )
        assert "❌ Error: If repeat_count is provided, repeat_frequency is required" in result

    @patch('tools.build')
    @patch('tools.get_credentials')
    def test_google_api_error_handling(self, mock_creds, mock_build):
        """Test handling of Google Calendar API errors"""
        from googleapiclient.errors import HttpError
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Simulate API error
        mock_response = MagicMock()
        mock_response.status = 403
        mock_service.events().insert().execute.side_effect = HttpError(
            resp=mock_response, 
            content=b'Forbidden'
        )
        
        result = create_event(
            summary="Test Meeting",
            start_time="2025-01-16 14:00",
            duration_minutes=60
        )
        
        assert "❌ Error creating event:" in result

    # Edge case tests
    def test_valid_minimal_event(self):
        """Test creating event with minimal valid parameters"""
        with patch('tools.build') as mock_build, patch('tools.get_credentials'):
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.events().insert().execute.return_value = {'htmlLink': 'test'}
            
            result = create_event(
                summary="Meeting",
                start_time="2025-01-16 14:00",
                duration_minutes=30
            )
            
            assert "✅" in result
            
            # Verify minimal fields were set correctly
            call_args = mock_service.events().insert.call_args[1]['body']
            assert call_args['summary'] == "Meeting"
            assert 'description' not in call_args  # Should not be included if empty
            assert 'location' not in call_args     # Should not be included if empty
            assert 'attendees' not in call_args    # Should not be included if None 