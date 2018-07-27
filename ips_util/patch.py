class Patch:
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