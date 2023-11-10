from datetime import datetime
from .facade_class import AbstractConvertApplication


class SetMeter(AbstractConvertApplication):

    def __init__(self, profile):
        super().__init__(profile)

    @staticmethod
    def confirm_datetime(current_data, current_time):

        slice_dt = f"{current_data} {current_time}"  # Время среза
        tmp_dt = slice_dt.split()

        tmp_date = tmp_dt[0].split('.')
        tmp_time = tmp_dt[1]

        if tmp_time == "00:00":
            tmp_time = "24:00"

        if len(tmp_date[2]) == 2:
            tmp_date[2] = f'20{tmp_date[2]}'

        tmp_date = ".".join(tmp_date)
        current_dt = f"{tmp_date} {tmp_time}"

        return current_dt

    async def make_report(self):

        if not self.txt_files:
            return []

        for file in self.txt_files:
            with open(file, encoding='windows-1251') as content:
                text = content.readlines()

            index = 0

            for line in text:
                if line.strip().startswith('Серийный номер счетчика'):
                    self.serial = line.strip().split()[3]
                elif line.strip().startswith('Счетчик №'):
                    self.serial = line.strip().split()[2]
                if "".join(line.strip().split()).startswith('ДатаВремя'):
                    index = text.index(line)

            if index == 0:
                self.bad_txt_files.append(file)
                continue

            slice_data = []

            try:
                dt_1 = datetime.strptime(text[index + 1].strip().split()[1].split('-')[1], "%H:%M")
                dt_2 = datetime.strptime(text[index + 2].strip().split()[1].split('-')[1],  "%H:%M")
            except ValueError:
                self.bad_txt_files.append(file)
                continue

            delta = str(int((dt_2 - dt_1).total_seconds() / 60))

            for line in text[index + 1:]:
                if line.startswith('=='):
                    break

                clear_line = line.strip().split()

                current_dt = self.confirm_datetime(clear_line[0], clear_line[1].split('-')[1])

                try:
                    active_positive = clear_line[2].replace(",", ".")
                    active_negative = clear_line[3].replace(",", ".")
                    reactive_positive = clear_line[4].replace(",", ".")
                    reactive_negative = clear_line[5].replace(",", ".")
                except IndexError:
                    active_positive = '000.0000'
                    active_negative = '000.0000'
                    reactive_positive = '000.0000'
                    reactive_negative = '000.0000'

                slice_data.append([delta, f'{current_dt}', active_positive, active_negative, reactive_positive,
                                   reactive_negative])

            self.all_data.append(
                {
                    self.serial: slice_data
                }
            )

        await self.create_report(self.all_data)
        return self.all_data


# if __name__ == '__main__':
#
#     mercury = SetMeter(os.path.join(os.getcwd(), 'Профили'))
#     data = mercury.get_data()
#     print(len(data))
#     print(f"Всего файлов: {len(mercury.all_files)}")
#     print(f"Текстовых файлов: {len(mercury.txt_files)}")
#     print(f"Невалидных файлов: {len(mercury.bad_files)} - {mercury.bad_files}")
#     # pprint(data)
#
#     with open('data.json', 'w', encoding='utf8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)
