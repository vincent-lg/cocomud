"""Test script, to try to play the sound.ogg file, which should be in the root directory."""

import sys
import time

import pybass

if not pybass.BASS_Init(-1, 44100, 0, 0, 0):
    print("An error ocurred during initialization.")
    sys.exit(1)

plugins = {}
plugins['aac'] = (pybass.BASS_PluginLoad(b'bass_aac.dll', 0), '|AAC|*.aac')
plugins['ac3'] = (pybass.BASS_PluginLoad(b'bass_ac3.dll', 0), '|AC3|*.ac3')
plugins['aix'] = (pybass.BASS_PluginLoad(b'bass_aix.dll', 0), '|AIX|*.aix')
plugins['ape'] = (pybass.BASS_PluginLoad(b'bass_ape.dll', 0), '|APE|*.ape')
plugins['mpc'] = (pybass.BASS_PluginLoad(b'bass_mpc.dll', 0), '|MPC|*.mpc')
plugins['ofr'] = (pybass.BASS_PluginLoad(b'bass_ofr.dll', 0), '|OFR|*.ofr')
plugins['spx'] = (pybass.BASS_PluginLoad(b'bass_spx.dll', 0), '|SPX|*.spx')
plugins['tta'] = (pybass.BASS_PluginLoad(b'bass_tta.dll', 0), '|TTA|*.tta')
plugins['cda'] = (pybass.BASS_PluginLoad(b'basscd.dll', 0), '|CDA|*.cda')
plugins['flac'] = (pybass.BASS_PluginLoad(b'bassflac.dll', 0), '|FLAC|*.flac')
plugins['wma'] = (pybass.BASS_PluginLoad(b'basswma.dll', 0), '|WMA, WMV|*.wma;*.wmv')

print(f"Current volume: {pybass.BASS_GetVolume()}")

flags = 0
file_name = "sound.ogg"
pybass.BASS_CHANNELINFO._fields_.remove(('filename', pybass.ctypes.c_char_p))
pybass.BASS_CHANNELINFO._fields_.append(('filename', pybass.ctypes.c_wchar_p))
handle = pybass.BASS_StreamCreateFile(False, file_name.encode(), 0, 0, flags)
pybass.BASS_ChannelPlay(handle, False)

time.sleep(15)
