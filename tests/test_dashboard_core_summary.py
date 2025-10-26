import pytest

from src.ui.dashboard_manager import DashboardManager

class DummySM:
    def get_all_systems(self):
        return {}

class DummyClient:
    def __init__(self, company_name, satisfaction):
        self.company_name = company_name
        self.satisfaction = satisfaction

class DummyGameState:
    def __init__(self):
        self.current_money = 10000.0
        self.clients = [DummyClient('Acme', 0.85), DummyClient('Beta', 0.6)]
        self.specialists = []
        self.incidents = []
    def get_game_summary(self):
        return {
            'current_money': self.current_money,
            'pending_incidents_count': 0,
            'specialists_count': len(self.specialists),
            'game_time': 123.0
        }


def test_core_summary_present_and_lines():
    sm = DummySM()
    gs = DummyGameState()
    dm = DashboardManager(system_manager=sm)
    state = dm.get_dashboard_layout(gs)

    assert state.summaries, "Dashboard summaries should not be empty"
    # First summary should be core_summary
    name, summary = state.summaries[0]
    assert name == 'core_summary'
    assert any('Budget' in line for line in summary.lines), "Core summary should include Budget line"
    assert any('Clients' in line for line in summary.lines), "Core summary should include Clients line"
