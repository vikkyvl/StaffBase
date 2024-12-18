import unittest
from unittest.mock import MagicMock, patch
from databases.redisDB import Redis


class TestRedis(unittest.TestCase):

    def setUp(self):
        self.mock_redis = MagicMock()

        with patch('redis.Redis', return_value=self.mock_redis):
            self.redis_client = Redis()

    def test_add_employee(self):
        user_info = MagicMock()
        user_info.get_login.return_value = 'john_doe'
        user_info.get_ID.return_value = '123'
        user_info.get_password.return_value = 'password123'

        self.redis_client.add_employee(user_info)

        self.mock_redis.hset.assert_called_once_with(
            'user:john_doe',
            mapping={"id": '123', "password": 'password123'}
        )

    def test_is_exist_user(self):
        self.mock_redis.hexists.return_value = True

        result = self.redis_client.is_exist_user('john_doe')

        self.assertEqual(result, 1)
        self.mock_redis.hexists.assert_called_once_with('user:john_doe', 'password')

    def test_update_employee_password(self):
        self.mock_redis.hexists.return_value = True

        result = self.redis_client.update_employee_password('john_doe', 'new_password')

        self.assertEqual(result, 1)
        self.mock_redis.hset.assert_called_once_with('user:john_doe', 'password', 'new_password')

    def test_update_employee_login(self):
        self.mock_redis.hexists.side_effect = [True, False]
        self.mock_redis.hgetall.return_value = {"id": '123', "password": 'password123'}

        result = self.redis_client.update_employee_login('old_login', 'new_login')

        self.assertEqual(result, 1)
        self.mock_redis.hgetall.assert_called_once_with('user:old_login')
        self.mock_redis.delete.assert_called_once_with('user:old_login')
        self.mock_redis.hset.assert_called_once_with('user:new_login', mapping={"id": '123', "password": 'password123'})

    def test_delete_employee(self):
        self.mock_redis.hexists.return_value = True

        result = self.redis_client.delete_employee('john_doe')

        self.assertEqual(result, 1)
        self.mock_redis.delete.assert_called_once_with('user:john_doe')

    def test_get_all_users(self):
        self.mock_redis.keys.return_value = ['user:john_doe', 'user:jane_doe']
        self.mock_redis.hgetall.side_effect = [
            {"id": '123', "password": 'password123'},
            {"id": '456', "password": 'password456'}
        ]

        result = self.redis_client.get_all_users()

        expected_result = [
            {"id": '123', "login": 'john_doe', "password": 'password123'},
            {"id": '456', "login": 'jane_doe', "password": 'password456'}
        ]

        self.assertEqual(result, expected_result)
        self.mock_redis.keys.assert_called_once_with('user:*')
        self.mock_redis.hgetall.assert_any_call('user:john_doe')
        self.mock_redis.hgetall.assert_any_call('user:jane_doe')


if __name__ == '__main__':
    unittest.main()
