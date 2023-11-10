from lxml import html
from lxml.etree import ParserError
from .facade_class import AbstractConvertApplication


class Mercury(AbstractConvertApplication):

    def __init__(self, profile):
        super().__init__(profile)

    @staticmethod
    def group(iterable, count):
        return zip(*[iter(iterable)] * count)

    @staticmethod
    def confirm_datetime(current_data, current_time):

        slice_dt = f"{current_data} {current_time}"  # Время среза
        try:
            tmp_dt = slice_dt.split()

            tmp_date = tmp_dt[0].split('.')
            tmp_time = tmp_dt[1]

            if tmp_time == "00:00":
                tmp_time = "24:00"

            if len(tmp_date[2]) == 2:
                tmp_date[2] = f'20{tmp_date[2]}'

            tmp_date = ".".join(tmp_date)
            current_dt = f"{tmp_date} {tmp_time}"
        except IndexError:
            return ""

        return current_dt

    def find_tag(self, file):

        with open(file, encoding='windows-1251') as content:
            try:
                dom = html.fromstring(content.read().lower())
                td = dom.xpath("//td")
            except (AttributeError, ParserError):
                self.bad_html_files.append(file)
                return "", []

            try:
                serial = dom.xpath("//h2")[0].text.split("серийный номер - ")[1][:8]
            except (AttributeError, IndexError):
                self.bad_html_files.append(file)
                return "", []

        profile_data = list(self.group(td, 10))

        return serial, profile_data

    async def make_report(self):

        if not self.html_files:
            return []

        for file in self.html_files:
            self.serial, profile_data = self.find_tag(file)

            slice_profile = []

            if not profile_data:
                continue

            for t in profile_data:
                p_plus = t[1].text
                p_minus = t[2].text
                q_plus = t[3].text
                q_minus = t[4].text
                current_time = t[5].text
                current_data = t[6].text
                integration = t[7].text

                if not current_time or not current_data:
                    break

                current_dt = self.confirm_datetime(current_data, current_time)
                slice_profile.append([integration, current_dt, p_plus, p_minus, q_plus, q_minus])

            self.all_data.append(
                {
                    self.serial: slice_profile
                }
            )

        await self.create_report(self.all_data)
        return self.all_data


# if __name__ == '__main__':
#
#     mercury = Mercury(os.path.join(os.getcwd(), 'Профили'))
#     controller = Controller(meter_obj=mercury)
#     data = controller.meter_obj.get_data()
#     pprint(data)
#
#     with open('data.json', 'w', encoding='utf8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)
