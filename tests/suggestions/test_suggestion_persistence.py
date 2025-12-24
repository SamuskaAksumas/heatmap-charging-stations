import json
import pytest
from unittest.mock import patch, mock_open
from src.domain.events.suggestion_handled import save_suggestion

def test_suggestion_save_event():
    """
    The Ultimate Standard: Mocking 'open' so we don't touch the real JSON file.
    """
    sample_input = {
        "plz": "10117",
        "address": "Friedrichstraße",
        "reason": "High traffic area"
    }

    # We mock 'open' and 'load_suggestions'
    # 1. load_suggestions returns [] so we start fresh
    # 2. mock_open captures everything written to the file
    with patch("src.domain.events.suggestion_handled.load_suggestions", return_value=[]), \
         patch("builtins.open", mock_open()) as mocked_file:
        
        # ACT
        save_suggestion(sample_input)
        
        # ASSERT
        # Verify that 'open' was called to write ('w') the file
        mocked_file.assert_called()
        
        # Get the data that was actually "written" to the fake file
        # We combine all chunks written to the file into one string
        handle = mocked_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        
        # Parse it back to JSON to check the content
        saved_json = json.loads(written_data)
        
        assert len(saved_json) == 1
        assert saved_json[0]['plz'] == "10117"
        assert saved_json[0]['status'] == "pending"
        assert "id" in saved_json[0]
        assert "timestamp" in saved_json[0]