# tests/unit/test_service_options.py
import pytest
from unittest.mock import MagicMock, patch
from robin_stocks_mcp.services.options import OptionsService
from robin_stocks_mcp.robinhood.client import RobinhoodClient
from robin_stocks_mcp.robinhood.errors import InvalidArgumentError, RobinhoodAPIError


def test_service_initialization():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    assert service.client == mock_client


def test_get_options_chain_requires_symbol():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    with pytest.raises(InvalidArgumentError, match="Symbol is required"):
        service.get_options_chain("")


def test_get_options_chain_with_expiration_date():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    mock_options_data = [
        {
            'chain_symbol': 'AAPL',
            'strike_price': '150.00',
            'type': 'call',
            'bid_price': '5.50',
            'ask_price': '5.75',
            'open_interest': '1000',
            'volume': '500'
        },
        {
            'chain_symbol': 'AAPL',
            'strike_price': '155.00',
            'type': 'put',
            'bid_price': '3.50',
            'ask_price': '3.75',
            'open_interest': '800',
            'volume': '300'
        }
    ]
    
    with patch('robin_stocks_mcp.services.options.rh') as mock_rh:
        mock_rh.find_options_by_expiration.return_value = mock_options_data
        
        contracts = service.get_options_chain('AAPL', '2026-03-20')
        
        assert len(contracts) == 2
        assert contracts[0].symbol == 'AAPL'
        assert contracts[0].strike == 150.0
        assert contracts[0].type == 'call'
        assert contracts[0].bid == 5.50
        assert contracts[0].ask == 5.75
        assert contracts[0].open_interest == 1000
        assert contracts[0].volume == 500
        assert contracts[0].expiration == '2026-03-20'
        
        assert contracts[1].symbol == 'AAPL'
        assert contracts[1].strike == 155.0
        assert contracts[1].type == 'put'
        
        mock_rh.find_options_by_expiration.assert_called_once_with('AAPL', expirationDate='2026-03-20')


def test_get_options_chain_without_expiration_date():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    mock_chains = {
        'expiration_dates': ['2026-03-20', '2026-04-17']
    }
    
    mock_options_data = [
        {
            'chain_symbol': 'AAPL',
            'strike_price': '150.00',
            'type': 'call',
            'bid_price': '5.50',
            'ask_price': '5.75',
            'open_interest': '1000',
            'volume': '500'
        }
    ]
    
    with patch('robin_stocks_mcp.services.options.rh') as mock_rh:
        mock_rh.get_chains.return_value = mock_chains
        mock_rh.find_options_by_expiration.return_value = mock_options_data
        
        contracts = service.get_options_chain('AAPL')
        
        assert len(contracts) == 1
        assert contracts[0].expiration == '2026-03-20'
        
        mock_rh.get_chains.assert_called_once_with('AAPL')
        mock_rh.find_options_by_expiration.assert_called_once_with('AAPL', expirationDate='2026-03-20')


def test_get_options_chain_empty_expirations():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    mock_chains = {
        'expiration_dates': []
    }
    
    with patch('robin_stocks_mcp.services.options.rh') as mock_rh:
        mock_rh.get_chains.return_value = mock_chains
        
        contracts = service.get_options_chain('AAPL')
        
        assert len(contracts) == 0
        mock_rh.find_options_by_expiration.assert_not_called()


def test_get_options_chain_api_error():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    with patch('robin_stocks_mcp.services.options.rh') as mock_rh:
        mock_rh.find_options_by_expiration.side_effect = Exception("API Error")
        
        with pytest.raises(RobinhoodAPIError, match="Failed to fetch options chain"):
            service.get_options_chain('AAPL', '2026-03-20')


def test_get_options_chain_calls_ensure_session():
    mock_client = MagicMock(spec=RobinhoodClient)
    service = OptionsService(mock_client)
    
    with patch('robin_stocks_mcp.services.options.rh') as mock_rh:
        mock_rh.find_options_by_expiration.return_value = []
        
        service.get_options_chain('AAPL', '2026-03-20')
        
        mock_client.ensure_session.assert_called_once()
