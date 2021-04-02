def install_engine_from_automation(ac_car_dir, automation_export_dir):
    """
    ai.ini:
      [GEARS]
        UP - What RPM AI should shift up
        DOWN - What RPM AI should shift down

    car.ini
      [BASIC] TOTALMASS (Take a value for the chassis and existing engine and adjust accordingly)
      [FUEL] CONSUMPTION
      [INERTIA] If the engine weight changes does this affect this?

    digital_instruments.ini
      [LED_0] - [LED_4] - used for showing shift lights

    drivetrain.ini
      [AUTOCLUTCH]
      [AUTO_SHIFTER]
      [DOWNSHIFT_PROTECTION] (dependant on quality?)

    engine.ini
      [HEADER]
        COAST_CURVE - coast curve. can define 3 different options (coast reference, coast values for mathematical curve, coast curve file)
      [ENGINE_DATA]
        INERTIA
        LIMITER
        MINIMUM (idle rpm)
      [COAST_REF]
        RPM - rev number reference
        TORQUE - engine braking torque value in Nm at rev number reference
        NON_LINEARITY - coast engine brake from ZERO to TORQUE value at rpm with linear (0) to fully exponential (1)
      [TURBO_N]
        LAG_DN - Interpolation lag used slowing down the turbo (0.96 - 0.99)
        LAG_UP - Interpolation lag used to spin up the turbo (0.96 - 0.999)
        MAX_BOOST - Maximum boost generated. This value is never exceeded and multiply the torque
                        like T=T*(1.0 + boost), a boost of 2 will give you 3 times the torque at a given rpm.
        WASTEGATE - Max level of boost before the wastegate does its things. 0 = no wastegate
        DISPLAY_MAX_BOOST - Value used by display apps
        REFERENCE_RPM= - The reference rpm where the turbo reaches maximum boost (at max gas pedal)
        GAMMA=5 - A value used to make the boost curve more exponential. 1 = linear
        COCKPIT_ADJUSTABLE=0

      fuel_cons.ini
        [FUEL_EVAL]
          KM_PER_LITER

      power.lut
        A lookup table for torque values after applying drivetrain losses. Each line is <RPM>|<TORQUE_NM>

      sounds.ini
      No idea how to update these yet. An example from tatuusfa01
      [BACKFIRE]
      MAXGAS=0.4
      MINRPM=3500
      MAXRPM=15000
      TRIGGERGAS=0.8
      VOLUME_IN=1.0
      VOLUME_OUT=0.5
      VOLUME_SCALE_OUT=6

    Warnings:
      if engine torque is greater than [CLUTCH].MAX_TORQUE in drivetrain.ini

    :param ac_car_dir:
    :param automation_export_dir:
    :return:
    """
    # Load existing car data
    # Replace engine data
    # update
    pass


def install_gearbox(car, gearbox_object):
    """
    Update pretty much everything in drivetrain.ini

    Create ratios.rto files for the gears available for the gearbox
    The files are of the form <ratio-name>|<ratio-value> e.g: F3B-12:38-INT|3.17

    Reference these ratio files in setup.ini
    [GEAR_N] where N is the gear number
      RATIOS=<ratios-file>
    [FINAL_GEAR_RATIO]
      RATIOS=<final.rto>

    In drivetrain.ini
    [GEARS]
     COUNT, GEAR_R, FINAL, GEAR_N (must be a gear for 1-N where N is COUNT)
     these should match up with a ratio lookup table file

    :param car:
    :param gearbox_object:
    :return:
    """
    pass
