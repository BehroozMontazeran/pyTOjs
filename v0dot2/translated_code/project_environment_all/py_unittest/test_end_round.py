import unittest
from unittest.mock import patch
from environment_all import GenericWorld

class TestGenericWorld(unittest.TestCase):

    def setUp(self):
        self.world = GenericWorld()

    def test_end_round(self):
        # Mocking dependencies
        mock_open = patch('builtins.open').start()
        mock_os = patch('os.path.exists').start()
        mock_os.return_value = False
        mock_logger = patch.object(self.world, 'logger').start()
        mock_agents = patch.object(self.world, 'agents').start()
        mock_active_agents = patch.object(self.world, 'active_agents').start()

        # Setting up test data
        self.world.round = 42
        agent1 = Mock(score=10, code_name='Agent1', train=True)
        agent2 = Mock(score=15, code_name='Agent2', train=False)
        self.world.agents = [agent1, agent2]
        self.world.active_agents = [agent1, agent2]
        self.world.args = Mock(save_replay=True)
        # Calling the method under test
        self.world.end_round()

        # Assertions
        mock_logger.info.assert_called_once_with('WRAPPING UP ROUND #42')
        mock_active_agents[0].add_event.assert_called_once_with(e.SURVIVED_ROUND)
        mock_active_agents[1].add_event.assert_called_once_with(e.SURVIVED_ROUND)
        mock_agents[0].round_ended.assert_called_once()
        mock_open.assert_called_once_with('elo/elo.log', 'a')
        mock_open().__enter__().write.assert_called_once_with('Agent1 < Agent2\n')
        mock_os.assert_called_once_with('elo')
        mock_os().mkdir.assert_called_once_with('elo')
        self.assertEqual(mock_os().mkdir.call_count, 1)
        self.assertEqual(mock_open().__exit__.call_count, 1)
        mock_open.reset_mock()
        mock_os.reset_mock()
        mock_logger.reset_mock()
        mock_agents.reset_mock()
        mock_active_agents.reset_mock()

        # Testing with different score comparison
        agent1 = Mock(score=10, code_name='Agent1', train=True)
        agent2 = Mock(score=10, code_name='Agent2', train=True)
        self.world.agents = [agent1, agent2]
        self.world.active_agents = [agent1, agent2]
        self.world.end_round()

        # Assertions
        mock_logger.info.assert_called_once_with('WRAPPING UP ROUND #42')
        mock_active_agents[0].add_event.assert_called_once_with(e.SURVIVED_ROUND)
        mock_active_agents[1].add_event.assert_called_once_with(e.SURVIVED_ROUND)
        mock_agents[0].round_ended.assert_called_once()
        self.assertEqual(mock_open.call_count, 0)
        self.assertEqual(mock_os.call_count, 0)

        # Cleaning up patches
        patch.stopall()

if __name__ == '__main__':
    unittest.main()