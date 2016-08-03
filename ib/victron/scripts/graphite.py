from time import sleep
from serial import Serial
from ib.victron.mk2 import MK2
from ib.victron.scripts.options import options
import graphitesend

'''
Sends inverter data to a local Graphite server.
'''

def main():
    port = Serial(options.port, options.baudrate, timeout=options.timeout)
    mk2 = MK2(port).start()

    g = graphitesend.init(graphite_server='127.0.0.1', group='mppt', prefix='')

    try:
        while True:
            out = dict()
            for key, val in mk2.ac_info().iteritems():
                out['ac_' + key] = val
                
            for key, val in mk2.dc_info().iteritems():
                out['dc_' + key] = val

            # Yes, these could be aggregated in Graphite.
            out['ac_power_draw'] = out['ac_uinv'] * out['ac_iinv']
            out['dc_power_draw'] = out['dc_ubat'] * out['dc_ibat']

            g.send_dict(out)

            sleep(1)
    except KeyboardInterrupt:
        pass
    port.close()

main()
