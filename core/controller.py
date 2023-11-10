import os
import json
from .facade_class import AbstractConvertApplication
from .convertor_mercury_class import Mercury
from .converter_set_class import SetMeter
import asyncio


class Controller:
    def __init__(self, meter_obj: AbstractConvertApplication):
        self.meter_obj = meter_obj


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    profile_path = os.path.join(os.getcwd(), 'Профили')

    mercury_meter = Mercury(profile_path)
    set_meter = SetMeter(profile_path)

    mercury_controller = Controller(meter_obj=mercury_meter)
    set_controller = Controller(meter_obj=set_meter)

    set_data = loop.create_task(set_controller.meter_obj.make_report())
    mercury_data = loop.create_task(mercury_controller.meter_obj.make_report())

    loop.run_until_complete(asyncio.wait([set_data, mercury_data]))

    with open('mercury_data.json', 'w', encoding='utf8') as mercury_file, open('set_data.json', 'w',
                                                                               encoding='utf8') as set_file:
        json.dump(mercury_data.result(), mercury_file, ensure_ascii=False, indent=4)
        json.dump(set_data.result(), set_file, ensure_ascii=False, indent=4)
