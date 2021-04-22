import sys
import sim_racing_tools.assetto_corsa.car as car
from sim_racing_tools.automation.fabricator.assetto_corsa import DefaultEngineFabricator

SUCCESS = 0
FAIL = 1


def clone_car(args):
    try:
        car.create_new_car_from_existing(args.new_brand_name, args.new_model_name, args.ac_car_folder)
        return SUCCESS
    except Exception as e:
        print(f"Failed to clone {args.ac_car_folder}")
        print(str(e), file=sys.stderr)
        return FAIL


def swap_engine(args):
    try:
        ac_car = car.load_car(args.ac_car_folder)
        ac_car.swap_engine(DefaultEngineFabricator().create_from_beamng_mod(args.exported_car_folder),
                           update_mass=args.update_mass,
                           old_engine_mass=args.mass_hint)
        ac_car.write()
    except Exception as e:
        print(f"Failed to swap engine from {args.exported_car_folder} to {args.ac_car_folder}")
        print(str(e), file=sys.stderr)
        return FAIL
