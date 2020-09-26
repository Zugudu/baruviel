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

whom = '''
<table class='w3-container w3-card w3-margin w3-table w3-bordered' style='width:800px;'>
<tr>
<td>Назва завдання</td>
<td>Хто призначив</td>
<td>Кому призначив</td>
<td>Стан</td>
</tr>
{}
</table>
'''

header = '''
<div class='w3-bar w3-blue'>
<div class='w3-bar-item'>Привіт {}</div>
<a href=/exit><div class='w3-bar-item w3-hover-red'>Вийти</div></a>
</div>
'''