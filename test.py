import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Função para logar no Duo (com melhorias)
def logar_duo(navegador, email, senha):
    navegador.get("https://admin-9f22894f.duosecurity.com/")

    esperar_elemento(navegador, By.ID, "login_emailaddress_field") # espera o elemento aparecer para depois armazenar na variável
    campo_email = navegador.find_element(By.ID, "login_emailaddress_field")
    campo_email.send_keys(email)

    esperar_elemento(navegador, By.ID, "login_continue_button")
    bt_continuar = navegador.find_element(By.ID, "login_continue_button")
    bt_continuar.click()

    esperar_elemento(navegador, By.ID, "login_password_field")
    campo_senha = navegador.find_element(By.ID, "login_password_field")
    campo_senha.send_keys(senha)

    esperar_elemento(navegador, By.ID, "login_perform_localpassword_primary_auth")
    bt_entrar = navegador.find_element(By.ID, "login_perform_localpassword_primary_auth")
    bt_entrar.click()

    esperar_elemento(navegador, By.XPATH, "//*[@id='duo-react-app']/div/div[1]/div/div/div/div[1]/div/ul/li[1]/a/div/div")
    bt_duo = navegador.find_element(By.XPATH, "//*[@id='duo-react-app']/div/div[1]/div/div/div/div[1]/div/ul/li[1]/a/div/div")
    bt_duo.click()
    time.sleep(10)
#função para 
def esperar_elemento(navegador, by, locator, timeout=10):
    try:
        WebDriverWait(navegador, timeout).until(EC.presence_of_element_located((by, locator)))
        return True  # Elemento encontrado
    except TimeoutException:
        print(f"Elemento com locator {locator} não encontrado após {timeout} segundos.")
        campo_busca = navegador.find_element(By.XPATH, "//*[@id='global-search-input']")
        campo_busca.clear()
        return False  # Elemento não encontrado

# Função para realizar as ações no site (com tratamento de erros, esperas e com feedback no console)
def pesquisa_usuário(navegador, dados):
    print("Iniciando o processo de geração de links Duo...") # Mensagem inicial
    total_usuarios = len(dados)
    erros = []
    erros_numeros_duplicados = [] #lista com logins que tem o número duplicado
    for index, dado in dados.iterrows():
        login = dado["LOGINS"]
        print(f"Processando usuário {index + 1} de {total_usuarios}: {login}") # Feedback do usuário atual
        try:
            esperar_elemento(navegador, By.XPATH, "//*[@id='global-search-input']")
            campo_busca = navegador.find_element(By.XPATH, "//*[@id='global-search-input']")
            campo_busca.click()
            campo_busca.send_keys(login)

            esperar_elemento(navegador, By.XPATH, "//*[@id='item_users_0']")
            campo_user = navegador.find_element(By.XPATH, "//*[@id='item_users_0']")
            campo_user.click()

            esperar_elemento(navegador, By.XPATH, "//td[7]/a")
            campo_acesso = navegador.find_elements(By.XPATH, "//td[7]/a")
            
            if len(campo_acesso) > 1: #confere se tem mais de um campo para ativação (mais de um número cadastrado)
                esperar_elemento(navegador, By.XPATH, "//td[8]/form/button")
                delete_buttons = navegador.find_elements(By.XPATH, "//td[8]/form/button") #encontra os botões de delete
                
                for i in range(len(delete_buttons) - 1): #percorre uma lista com os botões de delete e ignora o último (sendo o último o telefone correto)
                    try:
                        delete_button = delete_buttons[i]
                        delete_button.click()
                        esperar_elemento(navegador, By.XPATH, "//*[@id='magnetic-base-container']/main/div/div[2]/div/div[2]/div/div/div/div[3]/button[1]") 
                        remove_button = navegador.find_element(By.XPATH, "//*[@id='magnetic-base-container']/main/div/div[2]/div/div[2]/div/div/div/div[3]/button[1]") #encontra o botão de remove
                        remove_button.click()
                        time.sleep(1)
                    except Exception as e:
                        print(f"Erro ao tentar deletar número de telefone extra para {login}: {e}")
                        erros_numeros_duplicados.append({'login': login})
                    
                    esperar_elemento(navegador, By.XPATH, "//td[7]/a") #verifica a existência de um único número de telefone (o número correto)
                    campo_acesso = navegador.find_elements(By.XPATH, "//td[7]/a")
                    
                    if campo_acesso:
                        campo_acesso[-1].click() #clica no botão de ativação/reativação correto (o último telefone cadastrado)
                    else:
                        print(f"Erro: Nenhum número de telefone encontrado após a tentativa de exclusão para {login}")
                    time.sleep(1)
            else:
                campo_acesso = campo_acesso[0]
                campo_acesso.click()

            esperar_elemento(navegador, By.XPATH, "//*[@id='expire']")
            expire_field = navegador.find_element(By.XPATH, "//*[@id='expire']")
            expire_field.clear()
            time.sleep(0.5)
            expire_field.send_keys("72")

            esperar_elemento(navegador, By.XPATH, "//*[@id='regen_form']/div/div[2]/div[3]/button")
            bt_gera_codigo = navegador.find_element(By.XPATH, "//*[@id='regen_form']/div/div[2]/div[3]/button")
            bt_gera_codigo.click()

            esperar_elemento(navegador, By.XPATH, "//*[@id='installation_check']")
            bt_check = navegador.find_element(By.XPATH, "//*[@id='installation_check']")
            bt_check.click()

            esperar_elemento(navegador, By.XPATH, "//*[@id='form']/div/div[5]/button")
            bt_enviar = navegador.find_element(By.XPATH, "//*[@id='form']/div/div[5]/button")
            bt_enviar.click()

            print(f"Link enviado com sucesso para o usuário: {login}\n") # Feedback de sucesso

        except:
            erros.append({'login': login})
            

    if erros:
        print(f"Ocorreram {len(erros)} erros durante o processo.")
        print("Logins com erros:")
        for erro in erros:
            print(f"Usuário: {erro['login']}\n")
    else:
        print("Processo concluído sem erros!")

    if erros_numeros_duplicados:
        print(f"Existem {len(erros_numeros_duplicados)} com número duplicados no login.")
        print("Logins com erro ao deletar o número duplicados:")
        for numero_duplicado in erros_numeros_duplicados:
            print(f"Usuário: {numero_duplicado['login']}\n")
    else:
        print("Processo concluído sem erro na exclusão de números duplicados!")

# Variáveis
nome_do_arquivo = "massivo.xlsx"
dados = pd.read_excel(nome_do_arquivo)

#Configurando o Chrome para modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080") # Define o tamanho da janela (importante para headless)

navegador = webdriver.Chrome(options=chrome_options) #

logar_duo(navegador,"email", "senha")

pesquisa_usuário(navegador, dados)

navegador.quit()            
