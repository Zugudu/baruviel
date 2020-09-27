main = '''
<html>
<head>
<meta charset=utf8>
<meta name="viewport" content="width=device-width, initial-scale=1">
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

task_table = '''
<table class='w3-container w3-card w3-table w3-bordered' style='width:800px;'>
<tr class='w3-pale-yellow'>
<td>Назва завдання</td>
<td>Хто призначив</td>
<td>Кому призначив</td>
<td>Стан</td>
<td>Початок</td>
<td>Кінець</td>
</tr>
{}
</table>
'''


give_task = '''
<form method=POST class='w3-container w3-card w3-padding w3-margin' style='width:300px;'>
<label>Назва завдання*</label>
<input name='name' type='text' placeholder='Назва завдання' class='w3-input'>
<label>Кому*</label>
<select class='w3-select' name='whom'>
{}
</select>
<label>Дата початку</label>
<input name='start' type='date' class='w3-input'>
<label>Дата кінця</label>
<input name='end' type='date' class='w3-input'>
<button class='w3-btn w3-black w3-block w3-margin-top' type='submit'>Доручити</button>
</form>
'''


give_task_btn = "<a href='/task/give' class='w3-button w3-blue w3-hover-red w3-margin-bottom' style='width:300px;'>Доручити завдання</a>"


header = '''
<div class='w3-bar w3-blue w3-margin-bottom'>
<a href='/'><div class='w3-bar-item w3-hover-red'>Привіт {0}</div></a>
<a href='/task/whom/{1}'><div class='w3-bar-item w3-hover-red'>Отримані завдання</div></a>
<a href='/task/who/{1}'><div class='w3-bar-item w3-hover-red'>Доручені завдання</div></a>
<a href='/exit'><div class='w3-bar-item w3-hover-red'>Вийти</div></a>
</div>
'''