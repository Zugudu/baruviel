#codec=utf-8
import sqlite3
import csv
import opt
import pages
from os import path
from bottle import route, run, static_file, abort, post, request, redirect, error, response
from hashlib import sha3_256 as sha3


db = sqlite3.connect('db')
db.execute('pragma foreign_keys = 1')


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
	err = ('Введіть всі дані із зірочкою', 'Ви не маєте права на це')
	err_mes = ''
	try:
		err_num = int(request.query.err)
		if err_num >= 0 and err_num < len(err):
			err_mes = pages.error.format(err[err_num])
	except ValueError:
		pass
	sql.execute('select nick from user where id=?;', (session[1],))
	#return err_mes + pages.header.format(sql.fetchone()[0], session[1])
	#A VERY BAD IMPLEMENTATION DOWN
	if session[1] in (1, 2, 3):
		return err_mes + pages.header.format(sql.fetchone()[0], session[1], '<a href=\'/stat\'><div class=\'w3-bar-item w3-hover-red\'>Статистика сайту</div></a>')
	else:
		return err_mes + pages.header.format(sql.fetchone()[0], session[1], '')


@sql
def get_subtask_table(title, tasks, sql):
	list = ''
	for i in tasks:
		list += '<tr>'\
		'<td class="w3-border-right">{}</td>'\
		'<td class="w3-border-right">{}</td>'\
		'<td class="w3-border-right">{}</td>'\
		'<td class="w3-border-right">{}</td>'\
		'<td><a href="/subtask/{}" class="w3-button w3-black w3-hover-light-gray w3-block">Більше</a></td>'\
		'</tr>'.format(i[8], i[1], i[2], get_ico(i[4]), i[0])
	return pages.subtask_list.format(title, list)


@sql
def get_task_table(title, tasks, sql):
	list = ''
	for i in tasks:
		list += '<tr>'\
		'<td class="w3-border-right">{}</td>'\
		'<td class="w3-border-right">{}</td>'\
		'<td class="w3-border-right">{}</td>'\
		'<td><a href="/task/{}" class="w3-button w3-black w3-hover-light-gray w3-block">Більше</a></td>'\
		'</tr>'.format(i[1], i[2], get_ico(not sql.execute('select count(*) from v_done where id_task=?;', (i[0],)).fetchone()[0]), i[0])
	return pages.task_info.format(title, list)


### ROUTES ###


@route('/')
@sql
def index(sql):
	session = get_session(request)
	if session:
		#CLIENT PAGE
		sql.execute('select * from v_task ;')
		return opt.main(get_task_table('Останні завдання', sql.fetchall()), get_header(session, request))

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
			response.set_cookie('auth', _hash, max_age=432000)
			response.set_cookie('id_auth', str(sql.fetchone()[0]), max_age=432000)
		else:
			redirect('/?err=1')
	redirect('/')


@route('/task/<id:int>')
@sql
@login
def task_info(id, sql, session):
	sql.execute('select * from v_subtask where id_task=?;', (id, ))
	tasks = sql.fetchall()
	sql.execute('select name, who from task where id=?;', (id,))
	task = sql.fetchone()
	sql.execute('select who from task where id=?;', (id,))
	table = ''
	if sql.fetchone()[0] == session[1]:
		table = pages.give_task_btn.format('sub')
	table += get_subtask_table(task[0], tasks)
	if session[1] == task[1]:
		btn=pages.edit_task_btn.format('', id)
		btn+=pages.remove_task_btn.format(id)
	else:
		btn=''
	return opt.main(table+btn, get_header(session, request))


@route('/subtask/<id:int>')
@sql
@login
def task_info(id, sql, session):
	sql.execute('select * from v_subtask where id=?;', (id, ))
	task = sql.fetchone()
	if task[7] == session[1] or task[6] == session[1]:
		if task[4] == 0:
			status = 'Виконати завдання'
		else:
			status = 'Передумати'
		btn = pages.done_task_btn.format(id, status)

		if task[6] == session[1]:
			btn += pages.edit_task_btn.format('sub', id)
	else:
		btn = ''
	return opt.main(pages.subtask_info.format(task[1], task[3], task[2], get_ico(task[4]), btn), get_header(session, request))


@route('/task/list/who/<id:int>')
@sql
@login
def g_task_my(id, sql, session):
	sql.execute('select * from v_task where uid=?;', (id,))
	return opt.main(pages.give_task_btn.format('') + get_task_table('Створені мною завдання', sql.fetchall(),), get_header(session, request))


@route('/task/list/whom/<id:int>')
@sql
@login
def g_task_my(id, sql, session):
	sql.execute('select * from v_subtask where whom=?;', (id,))
	return opt.main(get_subtask_table('Доручені мені завдання', sql.fetchall()), get_header(session, request))


@route('/task/done/<id:int>')
@sql
@login
def task_done(id, sql, session):
	sql.execute('select * from v_subtask where id=?;', (id, ))
	task = sql.fetchone()
	if task[6] == session[1] or task[7] == session[1]:
		status = not task[4]
		sql.execute('update subtask set done=? where id=?;', (status, id))
		db.commit()
		redirect('/subtask/'+str(id))
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


@route('/subtask/edit/<id:int>')
@sql
@login
def subtask_edit(id, sql, session):
	sql.execute('select name, whom, id_task from subtask where id=?;', (id, ))
	task = sql.fetchone()
	sql.execute('select who from task where id=?;', (task[2],))
	if sql.fetchone()[0] == session[1]:
		user_list = ''
		task_list = ''
		sql.execute('select id, nick from user;')
		for i in sql.fetchall():
			if i[0] == task[1]:
				frmt = '<option value={} selected>{}</option>'
			else:
				frmt = '<option value={}>{}</option>'
			user_list += frmt.format(i[0], i[1])
		sql.execute('select id, name from task;')
		for i in sql.fetchall():
			if i[0] == task[2]:
				frmt = '<option value={} selected>{}</option>'
			else:
				frmt = '<option value={}>{}</option>'
			task_list += frmt.format(i[0], i[1])
		return opt.main(pages.give_subtask.format(task[0], user_list, task_list, 'Доручити'), get_header(session, request))
	else:
		redirect('/')


@post('/subtask/edit/<id:int>')
@sql
@login
def p_subtask_edit(id, sql, session):
	sql.execute('select who from v_subtask where id=?;', (id, ))
	task = sql.fetchone()
	if task[0] == session[1]:
		name = request.forms.name
		whom = request.forms.get('whom')
		task = request.forms.get('task')
		if name and whom and task:
			sql.execute('update subtask set name=?, whom=?, id_task=? where id=?;', (
				name,
				whom,
				task,
				id))
			db.commit()
			redirect('/subtask/' + str(id))
		else:
			redirect('/subtask/edit/' + str(id) + '?err=0')
	else:
		redirect('/subtask/edit/' + str(id) + '?err=1')


@route('/task/edit/<id:int>')
@sql
@login
def task_edit(id, sql, session):
	sql.execute('select name, who from task where id=?;', (id, ))
	task = sql.fetchone()
	if task[1] == session[1]:
		return opt.main(pages.give_task.format(task[0], 'Доручити'), get_header(session, request))
	else:
		redirect('/')


@post('/task/edit/<id:int>')
@sql
@login
def p_task_edit(id, sql, session):
	sql.execute('select who from task where id=?;', (id, ))
	task = sql.fetchone()
	if task[0] == session[1]:
		name = request.forms.name
		if name:
			sql.execute('update task set name=? where id=?;', (
				name,
				id))
			db.commit()
			redirect('/task/' + str(id))
		else:
			redirect('/task/edit/' + str(id) + '?err=0')
	else:
		redirect('/task/edit/' + str(id) + '?err=1')


@route('/subtask/give')
@sql
@login
def g_subtask_give(sql, session):
	user_list = ''
	task_list = ''
	sql.execute('select id, nick from user;')
	for i in sql.fetchall():
		user_list += '<option value={}>{}</option>'.format(i[0], i[1])
	sql.execute('select id, name from task;')
	for i in sql.fetchall():
		task_list += '<option value={}>{}</option>'.format(i[0], i[1])
	return opt.main(pages.give_subtask.format('', user_list, task_list, 'Доручити'), get_header(session, request))


@post('/subtask/give')
@sql
@login
def p_subtask_give(sql, session):
	name = request.forms.name
	whom = request.forms.get('whom')
	task = request.forms.get('task')
	sql.execute('select who from task where id=?;', (task,))
	if sql.fetchone()[0] == session[1]:
		if name and whom:
			sql.execute('insert into subtask values(null, ?, ?, 0, ?);', (
				name,
				whom,
				task))
			db.commit()
			redirect('/')
		else:
			redirect('/subtask/give?err=0')
	else:
		redirect('/')


@route('/task/give')
@sql
@login
def g_task_give(sql, session):
	return opt.main(pages.give_task.format('', 'Створити завдання'), get_header(session, request))


@post('/task/give')
@sql
@login
def p_task_give(sql, session):
	name = request.forms.name
	if name:
		sql.execute('insert into task values(null, ?, ?);', (
			name,
			session[1]))
		db.commit()
		redirect('/')
	else:
		redirect('/task/give?err=0')


@route('/exit')
@sql
@login
def exit(sql, session):
	response.set_cookie('auth', '')
	response.set_cookie('id_auth', '')
	sql.execute('delete from session where id=?;', (session[0],))
	db.commit()
	redirect('/')


@route('/stat')
@login
def statistic(session):
	if session[1] in (1, 2, 3):
		ret = ['', '']
		row = '<tr><td>{}</td><td>{} ({})</td></tr>'
		bad = '<span class=\'w3-text-red\'>{}</span>'
		good = '<span class=\'w3-text-green\'>+{}</span>'
		for i in range(2):
			last = 0
			with open(path.join('.', 'log/', str(i)), 'r') as fd:
				for r in fd:
					r = r.replace('\n', '').split('\t')
					delta = int(r[1]) - last
					last = int(r[1])
					if delta < 0:
						delta = bad.format(delta)
					else:
						delta = good.format(delta)
					ret[i] += row.format(r[0], r[1], delta)
		return opt.main(pages.stat.format(ret[0], ret[1]), get_header(session, request))
	else:
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