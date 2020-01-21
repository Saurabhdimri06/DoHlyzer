#!/usr/bin/env python
import argparse

from scapy.all import load_layer
from scapy.sendrecv import AsyncSniffer

from flow_session import generate_session_class


def create_sniffer(input_file, input_interface, output_mode, output_file):
    assert (input_file is None) ^ (input_interface is None)

    NewFlowSession = generate_session_class(output_mode, output_file)

    if input_file is not None:
        return AsyncSniffer(offline=input_file, filter='tcp port 443', prn=None, session=NewFlowSession)
    else:
        return AsyncSniffer(iface=input_interface, filter='tcp port 443', prn=None,
                            session=NewFlowSession)


def main():
    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-n', '--online', '--interface', action='store', dest='input_interface',
                             help='capture online data from INPUT_INTERFACE')
    input_group.add_argument('-f', '--offline', '--file', action='store', dest='input_file',
                             help='capture offline data from INPUT_FILE')

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument('-c', '--csv', '--flow', action='store_const', const='flow', dest='output_mode',
                              help='output flows as csv')
    output_group.add_argument('-s', '--json', '--segment', action='store_const', const='segment', dest='output_mode',
                              help='output flow segments as json')

    parser.add_argument('output', help='output file name (in csv mode) or directory (in json mode)')
    args = parser.parse_args()

    load_layer('tls')

    sniffer = create_sniffer(args.input_file, args.input_interface, args.output_mode, args.output)
    sniffer.start()

    try:
        sniffer.join()
    except KeyboardInterrupt as e:
        sniffer.stop()
    finally:
        sniffer.join()


if __name__ == '__main__':
    main()
