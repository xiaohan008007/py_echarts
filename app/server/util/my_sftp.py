import paramiko
import datetime


def test():
#创建sshclient对象
   ssh = paramiko.SSHClient()
#允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#调用connect方法连接服务器
   ssh.connect(hostname='10.0.0.36',port=58022)
   sftp = paramiko.SFTPClient.from_transport(ssh)
   sftp.get(server_file, local_file)
   input_command = input('ls')
#执行命令，输出结果在stdout中，如果是错误则放在stderr中
   stdin,stdout,stderr = ssh.exec_command(input_command)
   print(stdout)

def upload_action(IP, User, Password, local_file, server_file):
    try:
        terminal = paramiko.Transport(IP, 58022)
        terminal.connect(username=User, password=Password)
        sftp = paramiko.SFTPClient.from_transport(terminal)
        sftp.put(local_file, server_file)
        terminal.close()
    except Exception as e:
        print(e)
        raise
    return


def download_action(IP, User, Password, local_file, server_file):
    try:
        #key = paramiko.RSAKey.from_private_key_file(pkey_path)
        terminal = paramiko.Transport(IP, 58022)
        terminal.connect(username=User, password=Psssword)
        sftp = paramiko.SFTPClient.from_transport(terminal)
        sftp.get(server_file, local_file)
        terminal.close()
    except Exception as e:
        print(e)
        raise
    return

import time
if __name__ == '__main__':
    hour = time.strftime("%H", time.localtime())
    if int(hour) < 19:
        print(hour)
#     time.sleep()
#     now_time = datetime.datetime.now().strftime('%Y-%m-%d %T')
#     print(now_time)
#     #test()
#     #download_action('10.0.0.36', 'bohan', '80231886', 'testfile.zip', '/home/patch/tts-douyin-daren-web/static-2019-08-17_100894.zip')
#     ssh = paramiko.SSHClient()
# #允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect("10.0.0.36", port=58022)
#
#     ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('pwd')
#     print(3)
#     print(''.join(ssh_stdout.readlines()))
#     print()
#     sftp = ssh.open_sftp()
    #sftp.get('/home/patch/tts-douyin-daren-web/static-2019-08-17_100894.zip', 'tttt.zip')
    #sftp.put('tttt.zip', 'ttt1.zip')
    #ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls /home')