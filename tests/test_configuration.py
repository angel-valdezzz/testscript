import pytest

from testscript.cli import main
from testscript.configuration import BROWSERS, validate_config


@pytest.mark.parametrize('provider,browser', [(p, b) for p, choices in BROWSERS.items() for b in sorted(choices)])
def test_supported_provider_browser(provider, browser):
    assert validate_config({'provider': provider, 'browser': browser})


@pytest.mark.parametrize('config,message', [
    ({'provider': []}, 'provider must'),
    ({'browser': []}, 'unavailable'),
    ({'provider': 'selenium', 'browser': 'webkit'}, 'unavailable'),
    ({'incognito': 'true'}, 'must be Bool'),
    ({'viewport_width': True}, 'positive Int'),
    ({'viewport_height': 0}, 'positive Int'),
    ({'timeout': -1}, 'positive number'),
    ({'maximize': True}, 'requires headless'),
    ({'maximize': True, 'headless': False, 'viewport_width': 1200}, 'explicit viewport'),
    ({'maximize': True, 'headless': False, 'browser': 'webkit'}, 'only supported'),
    ({'surprise': True}, 'Unknown configuration'),
])
def test_invalid_configuration(config, message):
    with pytest.raises(ValueError, match=message):
        validate_config(config)


def test_cli_overrides_config_before_validation(tmp_path):
    config = tmp_path / 'testscript.toml'
    config.write_text('[testscript]\nprovider="selenium"\nbrowser="webkit"\nheadless=true\n')
    script = tmp_path / 'test.tscr'
    script.write_text('test "Core" { expect true }')
    assert main(['run', str(script), '--config', str(config), '--browser', 'firefox',
                 '--no-incognito', '--viewport-width', '1024', '--viewport-height', '768',
                 '--output', str(tmp_path / 'results')]) == 0
    assert main(['run', str(script), '--config', str(config)]) == 2
