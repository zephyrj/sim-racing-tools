#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argcomplete
import argparse

parser = argparse.ArgumentParser(description='Tools for working with Assetto Corsa (AC) content')

subparsers = parser.add_subparsers(title='Commands')
parser_clone_car = subparsers.add_parser('clone-car',
                                         help="Clone a car from the AC cars directory. Note: You must have already "
                                              "extracted the data.acd file to a data directory")
parser_clone_car.add_argument("ac_car_folder",
                              help="The name of the folder inside the AC cars directory to clone")
parser_clone_car.add_argument("new_brand_name", help="The name of the brand the newly cloned car will have")
parser_clone_car.add_argument("new_model_name", help="Then name of the model the newly cloned car will have")

parser_swap_engine = subparsers.add_parser('swap-automation-engine',
                                           help="Takes an engine from an automation car exported to BeamNG, creates "
                                                "the AC engine parameter data and puts that data into the provided car "
                                                "folder")
parser_swap_engine.add_argument('ac_car_folder', help="The AC car to swap the engine into")
parser_swap_engine.add_argument('exported_car_folder',
                                help="The name of the folder in the BeamNG mod directory containing the BeamNG "
                                     "exported car with the engine")
parser_swap_engine.add_argument('-m', "--update-mass", action="store_true",
                                help="Will update the car mass based on the difference between the old "
                                     "and new engine")
parser_swap_engine.add_argument("--mass-hint", type=int,
                                help="If the engine in the car has no mass data (i.e. isn't an engine "
                                     "created from Automation data) then you have to provide a mass "
                                     "for the old engine if you want to update the car mass. The value "
                                     "of this parameter will be used as the old engine mass in this "
                                     "scenario - the values unit is Kg")
parser_swap_engine.add_argument('-c', '--use-csp-physics', action="store_true",
                                help="Allow use of custom shader patch physics extensions when creating engine data")
argcomplete.autocomplete(parser)


def main():
    import sys
    import sim_racing_tools.assetto_corsa.scripts.ac_tools_impl as ac_impl
    parser_clone_car.set_defaults(func=ac_impl.clone_car)
    parser_swap_engine.set_defaults(func=ac_impl.swap_engine)
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == '__main__':
    main()
