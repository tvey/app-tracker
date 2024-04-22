import aiohttp


class SiteMonitor:
    def __init__(self, url):
        self.url = url
        self.failure_count = 0
        self.is_up = True

    async def check(self, session):
        try:
            async with session.get(self.url) as r:
                if r.status == 200:
                    if not self.is_up:
                        self.is_up = True
                        return (self.url, True)
                    self.failure_count = 0
                else:
                    self.failure_count += 1
        except Exception as e:
            print(f'Error checking {self.url}: {e}')
            self.failure_count += 1

        if self.failure_count >= 3:
            if self.is_up:
                self.is_up = False
                return (self.url, False)
                print(f'{self.url} is not available')
        return None
