import json
import os

from paypalrestsdk import api


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")


def get_fixture(name):
	path = os.path.join(FIXTURES_DIR, name)
	with open(path, "r") as f:
		data = json.load(f)
	return data


class TestApi(api.Api):
	def get(self, action, headers=None, refresh_token=None):
		fixture_path = os.path.join(FIXTURES_DIR, "GET", action + ".json")
		if not os.path.exists(fixture_path):
			raise NotImplementedError("Missing fixture: %r" % (fixture_path))
		with open(fixture_path, "r") as f:
			data = json.load(f)
		return data

	def post(self, action, params=None, headers=None, refresh_token=None):
		print(repr(self.endpoint), repr(action), repr(headers), repr(refresh_token))
		raise NotImplementedError

	def put(self, action, params=None, headers=None, refresh_token=None):
		print(repr(self.endpoint), repr(action), repr(headers), repr(refresh_token))
		raise NotImplementedError

	def patch(self, action, params=None, headers=None, refresh_token=None):
		print(repr(self.endpoint), repr(action), repr(headers), repr(refresh_token))
		raise NotImplementedError

	def delete(self, action, headers=None, refresh_token=None):
		print(repr(self.endpoint), repr(action), repr(headers), repr(refresh_token))
		raise NotImplementedError


# Monkey-patch the paypalrestsdk global api object.
# That object is the entry point to all HTTP requests in the Paypal API.
# We replace it with a mock handler which returns on-disk data.
api.__api__ = TestApi(client_id=None, client_secret=None)
