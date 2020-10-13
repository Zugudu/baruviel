main = '''
<html>
<head>
<meta charset=utf8>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/png" href="/static/ico/logo.png">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<title>Барувіель</title>
</head>
<body>
<center>
{}
</center>
</body>
</html>
'''

login = '''
<form method=POST class='w3-container w3-card w3-padding w3-margin' style='width:300px;'>
<label>Лоґін</label>
<input name='login' type='text' placeholder='Лоґін' class='w3-input'>
<label>Пароль</label>
<input name='pass' type='password' placeholder='Пароль' class='w3-input'>
<button class='w3-btn w3-black w3-block w3-margin-top' type='submit'>Увійти</button>
</form>
'''

error = '''
<div class="w3-container w3-red w3-padding">{}</div>
'''


give_subtask = '''
<form method=POST class='w3-container w3-card w3-padding w3-margin' style='width:300px;'>
<label>Назва завдання*</label>
<input name='name' type='text' placeholder='Назва завдання' class='w3-input' value='{}'>
<label>Кому*</label>
<select class='w3-select' name='whom'>
{}
</select>
<label>До завдання*</label>
<select class='w3-select' name='task'>
{}
</select>
<button class='w3-btn w3-black w3-block w3-margin-top' type='submit'>{}</button>
</form>
'''

give_task = '''
<form method=POST class='w3-container w3-card w3-padding w3-margin' style='width:300px;'>
<label>Назва завдання*</label>
<input name='name' type='text' placeholder='Назва завдання' class='w3-input' value='{}'>
<button class='w3-btn w3-black w3-block w3-margin-top' type='submit'>{}</button>
</form>
'''


give_task_btn = "<a href='/{}task/give{}' class='w3-button w3-blue w3-hover-red w3-margin-bottom' style='width:300px;'>Доручити завдання</a>"
done_task_btn = "<a href='/task/done/{}' class='w3-button w3-block w3-blue w3-hover-red w3-margin-top' style='width:300px;'>{}</a>"
done_task_btn_short = "<a href='/task/done/{}' class='w3-button w3-block w3-blue w3-hover-red'>{}</a>"
remove_task_btn = "<a href='/task/remove/{}' class='w3-button w3-block w3-blue w3-hover-red w3-margin-top' style='width:300px;'>Видалити завдання</a>"
edit_task_btn = "<a href='/{}task/edit/{}' class='w3-button w3-block w3-blue w3-hover-red w3-margin-top' style='width:300px;'>Змінити завдання</a>"
edit_task_btn_short = "<a href='/{}task/edit/{}' class='w3-button w3-block w3-blue w3-hover-red'>Змінити</a>"


_task_info = '''
<table class='w3-container w3-card w3-table w3-bordered' style='width:800px;'>
<tr>
<td colspan={} class='w3-center'><h3>{}</h3></td>
</tr>
<tr class='w3-pale-yellow'>
{}
<td class='w3-border-right'><h4>{}</h4></td>
<td class='w3-border-right'><h4>Відповідальний</h4></td>
<td class='w3-border-right'><h4>Стан</h4></td>
<td class='w3-border-right'></td>{}
</tr>
{}
</table>
'''

task_info = _task_info.format(4, '{}', '', 'Завдання', '', '{}')
subtask_list = _task_info.format('{}', '{}', '<td class="w3-border-right"><h4>Завдання</h4></td>' , 'Підзавдання', '{}', '{}')


header = '''
<div class='w3-bar w3-blue w3-margin-bottom'>
<a href='/'><div class='w3-bar-item w3-hover-red'>Привіт {0}</div></a>
<a href='/task/list/whom/{1}'><div class='w3-bar-item w3-hover-red'>Отримані завдання</div></a>
<a href='/task/list/who/{1}'><div class='w3-bar-item w3-hover-red'>Доручені завдання</div></a>
{2}
<a href='/exit'><div class='w3-bar-item w3-hover-red'>Вийти</div></a>
</div>
'''


stat = '''
<div class='w3-row' style='width:600px;'>
<table class='w3-table w3-bordered w3-border w3-container w3-half w3-centered w3-striped'>
<tr>
<td colspan=2>UHENTAI</td>
</tr>{}
</table>
<table class='w3-table w3-bordered w3-border w3-container w3-half w3-centered w3-striped'>
<tr>
<td colspan=2>UMANGA</td>
</tr>{}
</table>
</div>
'''