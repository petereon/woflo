import logging

logger = logging.getLogger('woflo')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
