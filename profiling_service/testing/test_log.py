import logging

logging.basicConfig(filename='../logs/logging.log', level=logging.DEBUG)

for i in range(20):
    logging.debug(i)
