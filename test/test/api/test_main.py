# -*- coding: utf-8 -*-

import unittest
import json
import api.main as main

app = main.application

class TestAPIMain(unittest.TestCase):

	def setUp(self):
		self.app = app.test_client()

	def tearDown(self):
		pass

	def test_curtime(self):
		rv = self.app.get('/curtime')
		assert json.loads(rv.data)["time"] != None


if __name__ == '__main__':
	unittest.main()
