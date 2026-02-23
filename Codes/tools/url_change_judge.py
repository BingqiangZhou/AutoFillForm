
# 自定义等待条件，检查URL是否变为新的URL
class url_has_changed:
    def __init__(self, old_url):
        self.old_url = old_url

    def __call__(self, driver):
        return driver.current_url != self.old_url