"""
Copyright 2016 Deepgram

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import ast
import jinja2
from .engine import Engine

###############################################################################
def combine(value, new=None):
	""" Jinja2 filter which merges dictionaries.
	"""
	new = new or {}
	value = dict(value)
	value.update(new)
	return value

###############################################################################
def as_dict(value, key):
	""" Jinja2 filter which constructs a dictionary from a key/value pair.
	"""
	return {key : value}

###############################################################################
class JinjaEngine(Engine):
	""" An evaluation engine which uses Jinja2 for templating.
	"""

	###########################################################################
	@staticmethod
	def register_custom_filters(env):
		""" Adds our custom filters to the Jinja2 engine.

			Arguments
			---------

			env: jinja2.Environment instance. The environment to add the custom
				filters to.
		"""
		env.filters['basename'] = os.path.basename
		env.filters['dirname'] = os.path.dirname
		env.filters['splitext'] = os.path.splitext
		env.filters['combine'] = combine
		env.filters['as_dict'] = as_dict

	###########################################################################
	def __init__(self, *args, **kwargs):
		""" Creates a new Jinja2 templating engine.
		"""

		# Call the parent
		super().__init__(*args, **kwargs)

		# Create a Jinja2 environment. We could use jinja2.Template().render()
		# directly, but having an environment gives us more control over, e.g.,
		# custom filters.
		self.env = jinja2.Environment()

		# Registering custom filters is described here:
		#   http://jinja.pocoo.org/docs/dev/api/#custom-filters
		self.register_custom_filters(self.env)

		# Built-in Jinja2 filters are listed here:
		#   http://jinja.pocoo.org/docs/dev/templates/#builtin-filters

	###########################################################################
	def _evaluate(self, expression):
		""" Evaluates an expression in the current scope.

			# Arguments

			expression: str. The string to evaluate.

			# Return value

			The evaluated expression (some Python object/class).
		"""
		result = self.env.from_string(expression).render(**self._scope)

		# Jinja2's `render()` will return a string which is a valid Python
		# expression (e.g., passing it through `eval` will succeed). However,
		# if you reference, e.g., a list that Jinja renders, the list will get
		# printed as a string. So we use `ast.literal_eval()` to turn it back
		# into a Python object. This may have unintended consequences, such as
		# turning the literal string "None" into the `None` Python object.
		# But it's better than nothing.
		try:
			result = ast.literal_eval(result)
		except (ValueError, SyntaxError):
			pass

		return result

### EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF.EOF
