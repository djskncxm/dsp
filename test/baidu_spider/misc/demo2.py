from test.baidu_spider import settings

print(type(settings))

for name in dir(settings):
    if name.isupper():
        print(getattr(settings, name))
