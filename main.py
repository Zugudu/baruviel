#codec=utf-8
import sqlite3
import csv
import opt
import pages
from bottle import route, run, static_file, abort, post, request, redirect, error, response
from hashlib import sha3_256 as sha3


db = sqlite3.connect('db')


def db_work(func):
	def wrap(*a, **ka):
		cursor = db.cursor()
		ret = func(*a, sql=cursor, **ka)
		cursor.close()
		return ret
	return wrap
	
	
@route('/static/<file:path>')
def load_static(file):
	return static_file(file, 'static')


def hash(text):
	return sha3(str(text).encode('utf-8')).hexdigest()
	

@db_work
def test_login(request, sql):
	"""
	return session data or None
	"""
	if request.get_cookie('auth') and request.get_cookie('id_auth'):
		sql.execute('select * from session where id=?;', (request.get_cookie('id_auth'), ))
		res = sql.fetchone()
		if res is not None:
			ip = request['REMOTE_ADDR']
			agent = request.headers.get('User-Agent')
			if ip == res[2] and agent == res[3] and request.get_cookie('auth') == res[4]:
				return res
	return None


@route('/')
@db_work
def index(sql):
	res = test_login(request)
	if res:
		#CLIENT PAGE
		sql.execute('select nick from user where id=?;', (res[1],))
		ret = pages.header.format(sql.fetchone()[0])
		
		list = ''
		sql.execute('select name,who,whom,done from full_task where who_id=?;', (res[1], ))
		for i in sql.fetchall():
			if i[3] == 0:
				ico = '<img src=\'/static/ico/quest.svg\' width=32 height=32>'
			else:
				ico = '<img src=\'/static/ico/done.svg\' width=32 height=32>'
			list += '<tr>'\
			'<td>{}</td>'\
			'<td>{}</td>'\
			'<td>{}</td>'\
			'<td>{}</td>'\
			'</tr>'.format(i[0],i[1],i[2],ico)
		return opt.main(ret+pages.whom.format(list))
			
	#LOGIN PAGE
	err = ('Немає такого користувача', 'Неправильний пароль')
	try:
		err_num = int(request.query.err)
		if err_num >= 0 and err_num < len(err):
			return opt.err(err[err_num], pages.login)
	except ValueError:
		pass
	return opt.main(pages.login)

@post('/')
@db_work
def p_index(sql):
	sql.execute('SELECT pass from user where id=?;', (request.forms.get('login'),))
	res = sql.fetchone()
	if res is None:
		redirect('/?err=0')
	else:
		if hash(request.forms.get('pass')) == res[0]:
			ip = request['REMOTE_ADDR']
			agent = request.headers.get('User-Agent')
			_hash = hash(hash(hash(request.forms.get('pass'))+ip)+agent)
			sql.execute('insert into session values(null, ?, ?, ?, ?);', (request.forms.get('login'), ip, agent, _hash))
			db.commit()
			sql.execute('select id from session where id_user=? and ip=? and agent=?;', (request.forms.get('login'), ip, agent))
			response.set_cookie('auth', _hash)
			response.set_cookie('id_auth', str(sql.fetchone()[0]))
		else:
			redirect('/?err=1')
	redirect('/')
	
	
@route('/exit')
@db_work
def route(sql):
	res = test_login(request)
	if res:
		response.set_cookie('auth', '')
		response.set_cookie('id_auth', '')
		sql.execute('delete from session where id=?;', (res[0],))
		db.commit()
	redirect('/')


if __name__ == '__main__':
	#print(sha3('1'.encode('utf-8')).hexdigest())
	try:
		with open('conf.csv', 'r', newline='') as fd:
			CONF=csv.reader(fd).__next__()
	except FileNotFoundError:
		print('Config doesn\'t exists. Creating new...')
		CONF = ('wsgiref', '127.0.0.1', '80', False, True)
		with open('conf.csv', 'w', newline='') as fd:
			csv.writer(fd).writerow(CONF)
			
	print('RL: {} QT: {}'.format(CONF[4], CONF[3]))
	if CONF[0] == 'gevent':
		from gevent import monkey; monkey.patch_all()
		run(server=CONF[0],
			host=CONF[1],
			port=CONF[2],
			quiet=CONF[3],
			reloader=CONF[4],
			keyfile=CONF[5]+'privkey.pem',
			certfile=CONF[5]+'fullchain.pem')
	else:
		run(server=CONF[0],
			host=CONF[1],
			port=CONF[2],
			quiet=CONF[3],
			reloader=CONF[4])