import pytest
from unittest.mock import MagicMock, patch, ANY
from bot_engine import AIStudioBot

@pytest.fixture
def mock_browser_driver():
    with patch('bot_engine.BrowserDriver') as MockDriver:
        driver_instance = MockDriver.return_value
        # Mock the page object
        mock_page = MagicMock()
        driver_instance.page = mock_page
        yield driver_instance

def test_bot_initialization(mock_browser_driver):
    bot = AIStudioBot()
    assert bot.driver == mock_browser_driver

def test_ensure_connection_navigates_to_new_chat(mock_browser_driver):
    bot = AIStudioBot()
    # Mock page.url to something else initially
    mock_browser_driver.page.url = "about:blank"
    
    # Mock context pages return
    mock_context = MagicMock()
    mock_browser_driver.context = mock_context
    mock_context.pages = []
    mock_context.new_page.return_value = mock_browser_driver.page

    bot.ensure_connection()
    
    # Verification
    # Should create new page if none found
    mock_context.new_page.assert_called()
    mock_browser_driver.page.goto.assert_called_with("https://aistudio.google.com/prompts/new_chat")

def test_select_model_gemini_3_pro(mock_browser_driver):
    bot = AIStudioBot()
    mock_page = mock_browser_driver.page
    bot.page = mock_page # Manually set page as ensure_connection sets it
    
    # Scenario: Current model is NOT Gemini 3 Pro
    # Mock text_content of model selector to be something else
    mock_card = MagicMock()
    mock_card.text_content.return_value = "gemini-1.5-pro"
    
    mock_target_btn = MagicMock()
    
    # wait_for_selector side effects
    def side_effect(selector, timeout=None):
        if selector == "button.model-selector-card":
            return mock_card
        if "gemini-3-pro-preview" in selector:
            return mock_target_btn
        return MagicMock()
        
    mock_page.wait_for_selector.side_effect = side_effect
    
    bot.select_model()
    
    # Verify interaction
    # 1. Check current model
    mock_page.wait_for_selector.assert_any_call("button.model-selector-card", timeout=ANY)
    # 2. Click selector since it wasn't correct
    mock_card.click.assert_called()
    # 3. Click the specific model in the list
    mock_target_btn.click.assert_called()

def test_select_system_instruction(mock_browser_driver):
    bot = AIStudioBot()
    mock_page = mock_browser_driver.page
    bot.page = mock_page
    
    # Scenario: "note generator" is not selected
    # Mock dropdown text
    mock_card = MagicMock() # instruction card
    mock_dropdown = MagicMock() # dropdown trigger
    mock_dropdown.text_content.return_value = "Create new instruction"
    
    mock_option = MagicMock()
    
    def wait_side_effect(selector, timeout=None):
        if "system-instructions-card" in selector:
            return mock_card
        if ".mat-mdc-select-trigger" in selector:
            return mock_dropdown
        return MagicMock()

    mock_page.wait_for_selector.side_effect = wait_side_effect
    
    # Locator for option
    mock_page.locator.return_value.filter.return_value.first = mock_option
    
    bot.select_system_instruction()
    
    # Verify interaction
    # 1. Click card
    mock_card.click.assert_called()
    # 2. Check dropdown
    mock_dropdown.click.assert_called()
    # 3. Click option
    mock_option.click.assert_called()