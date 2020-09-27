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
	
	
def get_ico(status):
	if status == 0:
		return '<img src=\'/static/ico/quest.svg\' width=32 height=32>'
	else:
		return '<img src=\'/static/ico/done.svg\' width=32 height=32>'
	
	
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
def get_header(session, request, sql):
	err = ('Введіть всі дані із зірочкою',)
	err_mes = ''
	try:
		err_num = int(request.query.err)
		if err_num >= 0 and err_num < len(err):
			err_mes = pages.error.format(err[err_num])
	except ValueError:
		pass
	sql.execute('select nick from user where id=?;', (session[1],))
	return err_mes + pages.header.format(sql.fetchone()[0], session[1])
	
	
def get_task_table(tasks):
	list = ''
	for i in tasks:
		list += '<tr>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td>{}</td>'\
		'<td><a href=\'/task/{}\' class=\'w3-button w3-hover-blue\'>Більше</a></td>'\
		'</tr>'.format(i[0], i[1], i[2], get_ico(i[3]), i[6], i[7], i[8])
	return pages.task_table.format(list)


@route('/')
@sql
def index(sql):
	session = get_session(request)
	if session:
		#CLIENT PAGE
		sql.execute('select * from full_task;')
		return opt.main(get_task_table(sql.fetchall()), get_header(session, request))
			
	#LOGIN PAGE
	err = ('Немає такого користувача', 'Неправильний пароль')
	try:
		err_num = int(request.query.err)
		if err_num >= 0 and err_num < len(err):
			return opt.main(pages.error.format(err[err_num])+pages.login)
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
	
	
@route('/task/list/<which>/<id:int>')
@sql
@login
def g_task_my(which, id, sql, session):
	if which in ('who', 'whom'):
		sql.execute('select * from full_task where ' + which + '_id=?;', (id,))
		return opt.main(pages.give_task_btn + get_task_table(sql.fetchall()), get_header(session, request))
	redirect('/')
		
		
@route('/task/give')
@sql
@login
def g_task_give(sql, session):
	sql.execute('select id, nick from user;')
	user_list = ''
	for i in sql.fetchall():
		user_list += '<option value={}>{}</option>'.format(i[0], i[1])
	return opt.main(pages.give_task.format(user_list), get_header(session, request))
	
	
@post('/task/give')
@sql
@login
def p_task_give(sql, session):
	name = request.forms.name
	whom = request.forms.get('whom')
	if name and whom:
		sql.execute('insert into task values(null, ?, ?, ?, 0, ?, ?);', (
			name,
			session[1],
			whom,
			request.forms.get('start'),
			request.forms.get('end')))
		db.commit()
		redirect('/')
	else:
		redirect('/task/give?err=0')
	
	
@route('/task/done/<id:int>')
@sql
@login
def task_done(id, sql, session):
	sql.execute('select * from full_task where id=?;', (id, ))
	task = sql.fetchone()
	if task[4] == session[1] or task[5] == session[1]:
		if task[3] == 0:
			status = 1
		else:
			status = 0
		sql.execute('update task set done=? where id=?;', (status, id))
		db.commit()
		redirect('/task/'+str(id))
	else:
		redirect('/')
		
		
@route('/task/remove/<id:int>')
@sql
@login
def task_remove(id, sql, session):
	sql.execute('select who from task where id=?;', (id, ))
	task = sql.fetchone()
	if task[0] == session[1]:
		sql.execute('delete from task where id=?;', (id, ))
		db.commit()
	redirect('/')
		
		
@route('/task/<id:int>')
@sql
@login
def task_info(id, sql, session):
	sql.execute('select * from full_task where id=?;', (id, ))
	task = sql.fetchone()
	if task[4] == session[1] or task[5] == session[1]:
		if task[3] == 0:
			status = 'Виконати завдання'
		else:
			status = 'Передумати'
		btn = pages.done_task_btn.format(id, status)
		
		if task[4] == session[1]:
			btn += pages.remove_task_btn.format(id)
	else:
		btn = ''
	return opt.main(pages.task_info.format(task[0], task[1], task[2], get_ico(task[3]), task[6], task[7], btn), get_header(session, request))
	
	
@route('/exit')
@sql
@login
def exit(sql, session):
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