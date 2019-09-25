from datetime import datetime, date, timedelta
import pytz
import os
import time
import subprocess
import logging
from logging import handlers
from app.config import basedir

local = pytz.timezone("Asia/Shanghai")


################################################################################
# log相关
################################################################################
def init_logger():
    """

    :return:
    """
    root_logger = logging.getLogger(__name__)
    root_logger.setLevel(logging.DEBUG)

    rotate_handler = handlers.TimedRotatingFileHandler(basedir + "/log/mylog", when='H', interval=1,
                                                       backupCount=48)
    rotate_handler.suffix = "%Y%m%d-%H.log"
    rotate_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter("%(levelname)-8s %(asctime)s %(filename)s:%(lineno)d""]%(message)s")
    # rotate_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(rotate_handler)

    return root_logger


################################################################################
# 日期相关辅助函数
################################################################################
def return_day_list(input_list):
    """
    返回args element前的日期
    :param args:
    :return:
    """
    date_list = []
    for offset in input_list:
        tmp_date = datetime.combine(date.today() - timedelta(days=date.today().weekday() + offset), datetime.min.time())
        local_dt = local.localize(tmp_date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        date_list.append(utc_dt)
    return date_list


def timestamp():
    """Return the current timestamp as an integer."""
    return int(time.time())

# 把'2015-06-01'这种字符串转为datetime的date
# 把datetime的date转为'2015-06-01'这种格式字符串直接str(date)
def str2date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


# 获取当天日期字符串，2015-06-01
def today():
    return str(date.today())


# 获取前一天日期字符串，2015-05-31
def one_day_ago():
    return str(date.today() - timedelta(days=1))


# 获取n天前的日期字符串
def n_day_ago(n):
    return str(date.today() - timedelta(days=n))


# off_the_end这一天之前的n天日期字符串数组，不包含off_the_end，
# off_the_end为'2015-06-01'格式的字符串
def last_n_days(off_the_end, n):
    return [str(str2date(off_the_end) - timedelta(x)) for x in range(n, 0, -1)]


# 上个星期的日期字符串数组，从星期一开始
def days_of_last_week():
    today = date.today()
    first_day_of_this_week = today - timedelta(today.weekday())
    return last_n_days(str(first_day_of_this_week), 7)


################################################################################
# 文件系统相关辅助函数
################################################################################

# 检查文件夹是否存在，不存在的话创建，支持多级路径
def check_exist_or_make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


################################################################################
# 运行命令行相关辅助函数
################################################################################

# 运行命令行，进程启动起来后返回
# subprocess tutorial: http://pymotw.com/2/subprocess/
def run_cmd(cmd_str):
    cmd_lines = [line for line in cmd_str.splitlines() if len(line) > 0]
    cmd_str = ' \\\n'.join(cmd_lines)
    process = subprocess.Popen(cmd_str, shell=True)
    mesg = 'run command PPID=%s PID=%s CMD=%s' % (os.getpid(), process.pid, cmd_str)
    logging.debug(mesg)
    return process


# 等待一个运行中的进程结束
def wait_cmd(process, cmd_str):
    retcode = process.wait()
    if retcode != 0:
        mesg = 'fail with retcode(%s): %s' % (retcode, cmd_str)
        raise RuntimeError(mesg)


# 启动一个命令行进程，等运行结束后返回
def run_cmd_and_wait(cmd_str):
    process = run_cmd(cmd_str)
    wait_cmd(process, cmd_str)


# 启动一个命令行进程，读取stdout，等运行结束后返回
def run_cmd_and_read_stdout(cmd_str):
    cmd_lines = [line for line in cmd_str.splitlines() if len(line) > 0]
    cmd_str = ' \\\n'.join(cmd_lines)
    process = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
    mesg = 'run command PPID=%s PID=%s CMD=%s' % (os.getpid(), process.pid, cmd_str)
    logging.debug(mesg)
    for line in process.stdout:
        yield line.strip()
    wait_cmd(process, cmd_str)
