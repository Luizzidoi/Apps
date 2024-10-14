 # flet for graphics interface
import flet as ft
from flet import colors
import sqlite3

print('------------------- TASKS MANAGER -------------------------')

database_name = str(input('Qual o nome da base de dados que será criada? '))

class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.scroll = 'auto'
        self.page.bgcolor = ft.colors.GREEN_100
        self.page.window_width = 450
        self.page.window_height = 550
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'ToDo App'
        self.task = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(name, status)')
        self.results = self.db_execute('SELECT * FROM tasks')
        self.main_page()

    # Criar um banco de dados .db
    # query é um pedido de uma informação ou um dado
    def db_execute(self, query, params = []):
        with sqlite3.connect(database_name + '.db') as con:         # Abrir conexão e fechar conexão após executar
            cursor = con.cursor()                           # cursor faz a execução de uma query dentro do banco de dados 
            cursor.execute(query, params)
            con.commit()                                    # Salvar uma execução no banco de dados
             
            return cursor.fetchall()                        # retorna todas as linhas do banco de dados

    # Quando o usuário clica no checkbox, essa função atualiza a tela e o status no bd
    def checked(self, e):
        is_checked = e.control.value        # pega se o checkbox está true ou falso
        label = e.control.label

        # Altera o status das tasks no banco de dados
        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', params=[label])  # Procura no bd a task e altera seu status
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', params=[label])

        # Atauliza os resultados de cada tab de acordo com o checkbox
        if self.view == 'all':
            self.results = self.db_execute('SELECT * from tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=self.view)

        self.update_task_list()

    # Cria o checkbox com todas as tasks
    def tasks_container(self):
        # Se existir algum valor armazenado para cada linha de results, será criado os checkbox
        # res[0] busca a coluna name do bd e res[0] busca a coluna status
        return (ft.Container(height=self.page.height * 0.8,
                             content=ft.Column(controls=[ft.Checkbox(label=res[0],  
                                                                     on_change=self.checked, value=True if res[1] == 'complete' else False)
                                     for res in self.results if res])))

    # Joga para dentro da variável task o que foi digitado no input
    def set_value(self, e):
        self.task = e.control.value
        #print(self.task)
    
    # Atualizar a lista de tasks na tela
    def update_task_list(self):
        tasks = self.tasks_container()
        self.page.controls.pop()            # Deleta os elementos anteriores da tela
        self.page.add(tasks)
        self.page.update()

    # Adiciona no banco de dados e na lista após clicar no botão
    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'

        if name:
            # query = inserir dentro da tabelas tasks os valores 
            self.db_execute(query='INSERT INTO tasks VALUES(?,?)', params=[name, status])
            # Limpar dados de imput após o click em '+'
            input_task.value = ''

            self.results = self.db_execute('SELECT * FROM tasks')     # seleciona tudo o que tem no banco de dados (bd)
            # Atualizar a lista de tasks
            self.update_task_list()

    # Atualiza as tabs de acordo com o banco de dados
    def tabs_changed(self, e):
        if e.control.selected_index == 0:                               # Index 0 = primeira tab ('Todos')
            self.results = self.db_execute('SELECT * FROM tasks')       # seleciona tudo o que tem no banco de dados (bd)
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')   # seleciona todos os dados incompletos no bd
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')   # seleciona todos os dados incompletos no bd
            self.view = 'complete'

        self.update_task_list()

    def main_page(self):
        # Criando um barra de input e chama set value conforme digita a frase na barra de input
        input_task = ft.TextField(hint_text='Digite aqui uma tarefa',
                                  expand=True,
                                  on_change=self.set_value)

        # Barra de input + botão -> adiciona no banco de dados e na lista após clicar no botão (função add)
        input_bar = ft.Row(controls=[input_task, ft.FloatingActionButton(icon=ft.icons.ADD, 
                                                                         on_click=lambda e: self.add(e, input_task))])

        # selected_index faz com que a primeira tab esteja sempre seletionada
        tabs = ft.Tabs(selected_index = 0,
                       on_change=self.tabs_changed,
                       tabs=[ft.Tab(text='Todos'), ft.Tab(text='Em andamento'), ft.Tab(text='Finalizados')])
        
        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)


ft.app(target = ToDo)