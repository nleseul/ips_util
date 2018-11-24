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