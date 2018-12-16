import itertools

class Patch:
    @staticmethod
    def load(filename):
        loaded_patch = Patch()

        with open(filename, 'rb') as file:

            header = file.read(5)
            if header != 'PATCH'.encode('ascii'):
                raise Exception('Not a valid IPS patch file!')
            while True:
                address_bytes = file.read(3)
                if address_bytes == 'EOF'.encode('ascii'):
                    break
                address = int.from_bytes(address_bytes, byteorder='big')

                length = int.from_bytes(file.read(2), byteorder='big')
                rle_count = 0
                if length == 0:
                    rle_count = int.from_bytes(file.read(2), byteorder='big')
                    length = 1
                data = file.read(length)

                if rle_count > 0:
                    loaded_patch.add_rle_record(address, data, rle_count)
                else:
                    loaded_patch.add_record(address, data)

        return loaded_patch

    @staticmethod
    def create(original_data, patched_data):
        # The heuristics for optimizing a patch were chosen with reference to
        # the source code of Flips: https://github.com/Alcaro/Flips

        patch = Patch()

        run_in_progress = False
        current_run_start = 0
        current_run_data = bytearray()

        runs = []

        for index, (original, patched) in enumerate(zip(original_data, patched_data)):
            if not run_in_progress:
                if original != patched:
                    run_in_progress = True
                    current_run_start = index
                    current_run_data = bytearray([patched])
            else:
                if original == patched:
                    runs.append((current_run_start, current_run_data))
                    run_in_progress = False
                else:
                    current_run_data.append(patched)
        if run_in_progress:
            runs.append((current_run_start, current_run_data))

        for start, data in runs:
            grouped_byte_data = list([
                {'val': key, 'count': sum(1 for _ in group), 'is_last': False}
                for key,group in itertools.groupby(data)
            ])

            grouped_byte_data[-1]['is_last'] = True

            record_in_progress = bytearray()
            pos = start

            for group in grouped_byte_data:
                if len(record_in_progress) > 0:
                    # We don't want to interrupt a record in progress with a new header unless
                    # this group is longer than two complete headers.
                    if group['count'] > 13:
                        patch.add_record(pos, record_in_progress)
                        pos += len(record_in_progress)
                        record_in_progress = bytearray()

                        patch.add_rle_record(pos, bytes([group['val']]), group['count'])
                        pos += group['count']
                    else:
                        record_in_progress += bytes([group['val']] * group['count'])
                elif (group['count'] > 3 and group['is_last']) or group['count'] > 8:
                    # We benefit from making this an RLE record if the length is at least 8,
                    # or the length is at least 3 and we know it to be the last part of this diff.
                    patch.add_rle_record(pos, bytes([group['val']]), group['count'])
                    pos += group['count']
                else:
                    # Just begin a new standard record.
                    record_in_progress += bytes([group['val']] * group['count'])

            # Finalize any record still in progress.
            if len(record_in_progress) > 0:
                patch.add_record(pos, record_in_progress)

        return patch

    def __init__(self):
        self.records = []

    def add_record(self, address, data):
        record = {'address': address, 'data': data}
        self.records.append(record)

    def add_rle_record(self, address, data, count):
        if len(data) != 1:
            raise Exception('Data for RLE record must be exactly one byte! Received {0}.'.format(data))

        record = {'address': address, 'data': data, 'rle_count': count}
        self.records.append(record)

    def trace(self):
        print('''Start   End     Size   Data
------  ------  -----  ----''')
        for record in self.records:
            length = (record['rle_count'] if 'rle_count' in record else len(record['data']))
            data = ''
            if 'rle_count' in record:
                data = '{0} x{1}'.format(record['data'].hex(), record['rle_count'])
            elif len(record['data']) < 20:
                data = record['data'].hex()
            else:
                data = record['data'][0:24].hex() + '...'
            print('{0:06x}  {1:06x}  {2:>5}  {3}'.format(record['address'], record['address'] + length - 1, length, data))

    def encode(self):
        encoded_bytes = bytearray()

        encoded_bytes += 'PATCH'.encode('ascii')

        for record in self.records:
            encoded_bytes += record['address'].to_bytes(3, byteorder='big')
            if 'rle_count' in record:
                encoded_bytes += (0).to_bytes(2, byteorder='big')
                encoded_bytes += record['rle_count'].to_bytes(2, byteorder='big')
            else:
                encoded_bytes += len(record['data']).to_bytes(2, byteorder='big')
            encoded_bytes += record['data']

        encoded_bytes += 'EOF'.encode('ascii')

        return encoded_bytes

    def apply(self, in_data):
        out_data = bytearray(in_data)

        for record in self.records:
            if 'rle_count' in record:
                out_data[record['address'] : record['address'] + record['rle_count']] = b''.join([record['data']] * record['rle_count'])
            else:
                out_data[record['address'] : record['address'] + len(record['data'])] = record['data']

        return out_data