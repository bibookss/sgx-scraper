class TimeSales:
    def __init__(self, id, date, status='NOT_STARTED'):
        self.id = id
        self.date = date
        self.status = status
        self.base_url = 'https://links.sgx.com/1.0.0/derivatives-historical'
        self.urls = self.create_urls(id)

    def create_urls(self, id):
        target_files = ['WEBPXTICK_DT.zip', 'TickData_structure.dat', 'TC.txt', 'TC_structure.dat']

        urls = []
        for target_file in target_files:
            urls.append('{}/{}/{}'.format(self.base_url, id, target_file))

        return urls