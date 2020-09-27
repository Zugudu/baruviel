#codec=utf-8
import sqlite3
import csv
import opt
import pages
from bottle import route, run, static_file, abort, post, request, redirect, error, response
from hashlib import sha3_256 as sha3


db = sqlite3.connect('db')


def sql(func):
	def wrap(*a, **ka):
		cursor = db.cursor()
		ret = func(*a, sql=cursor, **ka)
		cursor.close()
		return ret
	return wrap
	
	
def login(func):
	def wrap(*a, **ka):
		session = get_session(request)
		if session:
			return func(*a, session=session, **ka)
		redirect('/')
	return wrap


def hash(text):
	return sha3(str(text).encode('utf-8')).hexdigest()
	
	
@route('/static/<file:path>')
def load_static(file):
	return static_file(file, 'static')
	

@sql
def get_session(request, sql):
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
	
	
@sql
def get_header(session, sql):
	sql.execute('select nick from user where id=?;', (session[1],))
	return pages.header.format(sql.fetchone()[0], session[1])
	
	
def get_task_table(tasks):
	list = ''
	for i in tasks:
		if i[3] == 0:
			ico = '<img src=\'/static/ico/quest.svg\' width=32 height=32>'
		else:
			ico = '<img src=\'/static/ico/done.svg\' width=32 height=32>'
		list += '<tr>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'</tr>'.format(i[0], i[1], i[2], ico, i[6], i[7])
	return pages.task_table.format(list)


@route('/')
@sql
def index(sql):
	session = get_session(request)
	if session:
		#CLIENT PAGE
		sql.execute('select * from full_task;')
		return opt.main(get_task_table(sql.fetchall()), get_header(session))
			
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
@sql
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
	
	
@route('/task/<which>/<id:int>')
@sql
@login
def task_my(which, id, sql, session):
	if which in ('who', 'whom'):
		sql.execute('select * from full_task where ' + which + '_id=?;', (id,))
		return opt.main(pages.give_task_btn + get_task_table(sql.fetchall()), get_header(session))
		
		
@route('/task/give')
@login
def task_my(session):
	return opt.main(pages.give_task.format(''), get_header(session))
	
	
@route('/exit')
@sql
@login
def route(sql, session):
	response.set_cookie('auth', '')
	response.set_cookie('id_auth', '')
	sql.execute('delete from session where id=?;', (session[0],))
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