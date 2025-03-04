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

import sys, logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)s: %(message)s')

import re, os.path, time
from sfz import SFZ


class SfzWriter():
	noteRegEx = re.compile(r'^(.+[-_])?(([abcdefgABCDEFG])([b#]?)(-?[0-9]))(v(([0-9]{1,3})|[LMHlmh]))?([-_][0-9]+)?\.wav$')
	numRegEx = re.compile(r'^(.+[-_])?([0-9]{1,3})(v(([0-9]{1,3})|[LMHlmh]))?([-_][0-9]+)?\.wav')

	def __init__(self, samples: tuple[str] = tuple()):
		self.regions = {}
		self.sfz = SFZ()
		self.samples = samples 
		self.name = 'Unnamed sound bank'
		self.instrument = 'Unnamed instrument'
		self.loop_mode = 'no_loop'


	@property
	def samples(self) -> tuple[str]:
		return self._samples
	
	
	@samples.setter
	def samples(self, samples: tuple[str]):		
		self._samples = samples
		self.evaluate_pitch()


	def evaluate_pitch(self):
		for fName in self.samples:
			base_name = os.path.basename(fName)
			match = self.noteRegEx.search(base_name)

			if match:
				noteNum = self.sfz.convertNote(match.group(2))

				if noteNum == None:
					logging.warning(f"Skipping file '{fName}': Unable to determine pitch from note name '{match.group(2)}'.")
					continue

				self.regions[noteNum] = fName
				continue

			match = self.numRegEx.search(base_name)

			if not match:
				logging.warning(f"Skipping file '{fName}': Unable to extract pitch information from filename '{base_name}'.")
				continue

			try:
				noteNum = int(match.group(2))
			except ValueError:
				logging.warning(f"Skipping file '{fName}': Invalid numeric value '{match.group(2)}' in filename.")
				continue

			if noteNum < 0 or noteNum > 127:
				logging.warning(f"Skipping file '{fName}': MIDI note number {noteNum} is out of valid range (0-127).")
				continue

			self.regions[noteNum] = fName


	def get_sound_bank(self):
		sound_bank = {
		'Name': self.name,
		'Date': time.strftime("%Y-%m-%d"),
		'instruments': [{
			'Instrument': self.instrument,
			'ampeg_release': '0.5',
			'groups': [{
				'loop_mode': self.loop_mode,
				'regions': []
				}]
			}]
		}

		return sound_bank


	def write(self, file_name: str):
		sound_bank = self.get_sound_bank()
		prevRegion = None

		for noteNum in sorted(self.regions.keys()):
			region = {}
			region['sample'] = self.regions[noteNum]
			region['pitch_keycenter'] = noteNum

			if prevRegion:
				gap = noteNum - prevRegion['pitch_keycenter'] - 1
				leftGap = gap // 2
				rightGap = gap - leftGap
				prevRegion['hikey'] = prevRegion['pitch_keycenter'] + leftGap
				region['lokey'] = noteNum - rightGap
				
			sound_bank['instruments'][0]['groups'][0]['regions'].append(region)
			prevRegion = sound_bank['instruments'][0]['groups'][0]['regions'][-1]

		self.sfz.soundBank = sound_bank
		self.sfz.exportSFZ(file_name)