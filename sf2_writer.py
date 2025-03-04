#
# Copyright 2016, roberto@zenvoid.org
# Modified by Aaron Mathew, 2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import re
from sfz import SFZ
from sf2 import SF2

class Sf2Writer:
	expected_input_format = 'sfz'
	expected_output_format = 'sf2'


	def __init__(self, input_file: str):
		self.input_file = input_file 

		sfz = SFZ()
		sfz.importSFZ(self.input_file)

		self.sound_bank = sfz.soundBank


	@property
	def input_file(self) -> str:
		return self._input_file
	

	@input_file.setter
	def input_file(self, input_file: str):
		match = re.search(r'\.([a-z0-9]+)$', input_file.lower())

		if not match:
			logging.error("Cannot determine format from file name: {}".format(input_file))
			raise ValueError(f"Invalid file name: {input_file}. No file extension found.")

		input_format = match.group(1)

		if input_format != self.expected_input_format:
			logging.error("Unknown or unsupported input format: {}".format(input_format))
			raise ValueError(f"Unsupported file format: {input_format}. Expected: {self.expected_input_format}")

		self._input_file = input_file


	@property
	def output_file(self):
		return self._output_file


	@output_file.setter
	def output_file(self, output_file: str):
		match = re.search(r'\.([a-z0-9]+)$', output_file.lower())

		if not match:
			logging.error("Cannot determine format from file name: {}".format(output_file))
			raise ValueError(f"Invalid file name: {output_file}. No file extension found.")

		output_format = match.group(1)

		if output_format != self.expected_output_format:
			logging.error("Unknown or unsupported output format: {}".format(output_format))
			raise ValueError(f"Unsupported file format: {output_format}. Expected: {self.expected_output_format}")
		
		self._output_file = output_file


	def write(self, output_file: str):
		self.output_file = output_file

		sf2 = SF2()
		sf2.exportSF2(self.sound_bank, self.output_file)