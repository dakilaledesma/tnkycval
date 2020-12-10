import subprocess

s = subprocess.check_output("ps ax|grep gunicorn", shell=True)
s = s.decode("utf-8").split("\n")

for nl in s:
	nl = nl.split(' ')
	nl = [v for v in nl if v != '']
	try:
		pid = nl[0]
	except IndexError:
		continue
	subprocess.run(f"kill -9 {pid}", shell=True)

subprocess.run("authbind gunicorn -w 3 --threads 2 -k gevent -b 0.0.0.0:80 server:app", shell=True)
