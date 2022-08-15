# Django
from django.conf import settings
from .models import Cookies, Planner
from django.contrib.auth.models import User
from django.core.mail import send_mail

# Web
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
from captcha.solver import solve_captcha
from captcha.assets import path_to_image

# Misc
import json
import os
import base64
import logging
from threading import Thread


def init_driver():
    options = Options()
    # Correr Headless
    options.headless = True
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Remote(command_executor=settings.SELENIUM_REMOTE_URL, options=options, desired_capabilities=DesiredCapabilities.CHROME)
    driver.implicitly_wait(5)
    return driver


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


def tomar_ramos(usuario, segunda_toma=False):  # Esto debe ser de una corrida ya que usa Sessions
    LOGIN_ENDPOINT = "https://ssb.uc.cl/ERPUC/twbkwbis.P_WWWLogin"
    MENU_ENDPOINT = "https://ssb.uc.cl/ERPUC/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu"
    cookie = Cookies.objects.filter(user=usuario).values('cookie_value')[0]['cookie_value']

    # Planner toma foreign id, entonces debemos obtenerlo
    id_usuario = User.objects.get(username=usuario).id
    try:
        estado = Planner.objects.get(user=id_usuario)
    except:
        return

    with open('base_cookie.json') as f:
        data = json.load(f)

    data[0]["value"] = cookie

    driver = init_driver()
    driver.get(LOGIN_ENDPOINT)
    for cookie in data:
        driver.add_cookie(cookie)
    driver.get(MENU_ENDPOINT)

    estado.estado_toma = 2
    estado.save()
    # Ya logeado, printea que va a tomar ramos y redirige el output
    print('\nChequeando credenciales...')

    try:
        # ENCONTRAR EL LINK DE AGREGAR O ELIMINAR CLASES
        agregar = driver.find_element(by=By.XPATH, value="/html/body/div[3]/table[1]/tbody/tr[2]/td[2]/a")
        print('¡Credenciales aceptadas!')
        agregar.click()
    except Exception as err:
        print(f"Debug: {err}")
        print(f'Las credenciales de {usuario} fueron rechazadas. No se pudieron tomar ramos')
        mail = User.objects.get(username=usuario).email
        send_mail(
        'AutoRamosWeb Error',
        'Hola, hemos detectado un fallo en tu toma de ramos: Credenciales UC rechazadas, , porfavor hacer relogin en: autoramos.xyz/relogin/',
        os.environ.get('EMAIL_HOST_USER'),
        [mail],
        fail_silently=False,
        )
        estado.estado_toma = 4
        estado.save()
        driver.quit()
        return
    logging.debug('\nTomando ramos...')


    def solve_period_captcha(captcha_button, text_c, usuario):
        # SOLUCIONAR CAPTCHA
        html = driver.page_source
        scrapeo_img_base64(html, usuario)
        captcha = path_to_image(f'{usuario}.dib') # Aqui se carga el captcha
        solution = solve_captcha(captcha) # Aqui se resuelve el captcha
        text_c.send_keys(solution)
        # APRETAR SUBMIT
        captcha_button.click()
    if not segunda_toma:
        try:
            # Ingresa a sector seleccionar periodo
            text_c = driver.find_element(by=By.XPATH, value='//*[@id="captcha_id"]')
            captcha_button = driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/p/button/div/div/div')
            solve_period_captcha(captcha_button, text_c, usuario)
        except NoSuchElementException as err:
            print("Captcha no encontrado, asumiendo estudiante PIANE")
            non_captcha_button = driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/input')
            non_captcha_button.click()
        except:
            # Asumiendo error con el resolvedor de captcha
            print(f'Error al seleccionar el semestre de {usuario}')
            mail = User.objects.get(username=usuario).email
            send_mail(
            'AutoRamosWeb Error',
            'Hola, hemos detectado un fallo en tu toma de ramos: Error al seleccionar el semestre, porfavor hacer relogin en: autoramos.xyz/relogin/',
            os.environ.get('EMAIL_HOST_USER'),
            [mail],
            fail_silently=False,
            )
            estado.estado_toma = 4
            estado.save()
            driver.quit()
            return

    # Seleccionar plan de estudios
    try:
        # Seleccionar primer plan de estudio
        select = Select(driver.find_element(By.XPATH, '//*[@id="st_path_id"]'))
        select.select_by_index(1)
        # Submit
        driver.find_element(By.XPATH, '/html/body/div[3]/form/input[19]').click()
    except:
        print(f'Error al seleccionar el plan de estudio de {usuario}')
        mail = User.objects.get(username=usuario).email
        send_mail(
        'AutoRamosWeb Error',
        'Hola, hemos detectado un fallo en tu toma de ramos: Error al seleccionar el plan de estudio | Fuera de horario de toma, porfavor hacer relogin en: autoramos.xyz/relogin/',
        os.environ.get('EMAIL_HOST_USER'),
        [mail],
        fail_silently=False,
        )
        estado.estado_toma = 4
        estado.save()
        driver.quit()
        return

    # Tomar ramos
    try:
        planner = estado
        crn_id1 = driver.find_element(by=By.XPATH, value='//*[@id="crn_id1"]')
        crn_id2 = driver.find_element(by=By.XPATH, value='//*[@id="crn_id2"]')
        crn_id3 = driver.find_element(by=By.XPATH, value='//*[@id="crn_id3"]')
        btn_cambios = driver.find_element(by=By.XPATH, value='/html/body/div[3]/form/input[19]')

        if not segunda_toma:
            crn_id1.send_keys(planner.nrc1)
            crn_id2.send_keys(planner.nrc2)
            crn_id3.send_keys(planner.nrc3)
            btn_cambios.click()
        else:
            failed_string = planner.failed
            print(f"DEBUG FAILED STRING: {failed_string}")
            if '1' in failed_string:
                crn_id1.send_keys(planner.nrc4)
            if '2' in failed_string:
                crn_id2.send_keys(planner.nrc5)
            if '3' in failed_string:
                crn_id3.send_keys(planner.nrc6)
            btn_cambios.click()
        html = driver.page_source
    except:
        print(f'Error al tomar los ramos de {usuario}')
        mail = User.objects.get(username=usuario).email
        send_mail(
        'AutoRamosWeb Error',
        'Hola, hemos detectado un fallo en tu toma de ramos: Error al tomar los ramos (NRC), porfavor hacer relogin en: autoramos.xyz/relogin/',
        os.environ.get('EMAIL_HOST_USER'),
        [mail],
        fail_silently=False,
        )
        estado.estado_toma = 4
        estado.save()
        driver.quit()
        return
    print(f'\n¡Ramos tomados para {usuario}!')

    # Check logged in or not
    cookie = str(driver.get_cookies()[0]["value"])

    # If cookie exists
    if cookie != 'set':
        if Cookies.objects.filter(user=usuario).exists():
            Cookies.objects.filter(user=usuario).update(cookie_value=cookie)
        else:
            Cookies.objects.create(user=usuario, cookie_value=cookie)

    failed_nrcs = scrapeo_pagina_final(html)
    if failed_nrcs and not segunda_toma:
        failed_ids = ""
        failed_nrcs_string = [str(x) for x in failed_nrcs]
        print(f"DEBUG FAILED STRINGS: {failed_nrcs_string}")
        if planner.nrc1 in failed_nrcs_string:
            failed_ids += "1"
        if planner.nrc2 in failed_nrcs_string:
            failed_ids += "2"
        if planner.nrc3 in failed_nrcs_string:
            failed_ids += "3"
        planner.failed = failed_ids
        planner.save()
        return tomar_ramos(usuario, True)
    else:
        estado.estado_toma = 3
        estado.save()
        driver.quit()

        failed_new = [str(x) for x in scrapeo_pagina_final(html)]
        nrc_tomados = []
        nrc_fallados = []

        if '1' in planner.failed:
            nrc_fallados.append(planner.nrc1)
            if planner.nrc4 not in failed_new:
                nrc_tomados.append(planner.nrc4)
            else:
                nrc_fallados.append(planner.nrc4)
        else:
            nrc_tomados.append(planner.nrc1)
        if '2' in planner.failed:
            nrc_fallados.append(planner.nrc2)
            if planner.nrc5 not in failed_new:
                nrc_tomados.append(planner.nrc5)
            else:
                nrc_fallados.append(planner.nrc5)
        else:
            nrc_tomados.append(planner.nrc2)
        if '3' in planner.failed:
            nrc_fallados.append(planner.nrc3)
            if planner.nrc6 not in failed_new:
                nrc_tomados.append(planner.nrc6)
            else:
                nrc_fallados.append(planner.nrc6)
        else:
            nrc_tomados.append(planner.nrc3)

        return finalizar_toma(usuario, nrc_tomados, nrc_fallados)


def finalizar_toma(usuario, nrc_tomados, nrc_fallados):
    print(f'\nFinalizando toma de ramos para {usuario}')
    # TODO Mail usuario de exito
    mail = User.objects.get(username=usuario).email
    send_mail(
    'AutoRamosWeb Exito',
    f"Hola, te informamos que hemos tomado tus ramos exitosamente! Los nrc's que fueron tomados son: {', '.join(nrc_tomados)} y los que fallaron fueron: {', '.join(nrc_fallados)}",
    os.environ.get('EMAIL_HOST_USER'),
    [mail],
    fail_silently=False,
    )

    # Eliminar planner
    user_id = User.objects.get(username=usuario).id
    Planner.objects.get(user=user_id).delete()

    # TODO Manejo de cookie
    cookie = Cookies.objects.get(user=usuario)
    # cookie.estado = False
    # cookie.save()
    # cookie.delete()
    return


# Login
def verificar_sesion(usuario, password) -> bool:
    # (True/False)
    LOGIN_ENDPOINT = "https://ssb.uc.cl/ERPUC/twbkwbis.P_WWWLogin"
    out: bool

    driver = init_driver()
    driver.get(LOGIN_ENDPOINT)
    username_field = driver.find_element(by=By.XPATH, value="//*[@id='UserID']")
    username_field.send_keys(usuario)

    password_field = driver.find_element(by=By.XPATH, value="/html/body/div[3]/form/table/tbody/tr[2]/td[2]/input")
    password_field.send_keys(password)

    access_button = driver.find_element(by=By.XPATH, value="/html/body/div[3]/form/p/input")
    access_button.click()

    # Check logged in or not
    cookie = str(driver.get_cookies()[0]["value"])

    # If cookie exists
    if cookie != 'set':
        if Cookies.objects.filter(user=usuario).exists():
            Cookies.objects.filter(user=usuario).update(cookie_value=cookie)
        else:
            Cookies.objects.create(user=usuario, cookie_value=cookie)
        out = True
    else:
        out = False

    driver.quit()
    return out

# TODO: Implementar que revise todas las cookies cada 30 minutos y de ahi saque las que estan expiradas
def revalidar_cookies():
    print(f"<><> Debug: revalidar_cookies llamado! <><>")

    with open('base_cookie.json') as f:
            data = json.load(f)

    def validate_cookie(item, data=data):
        LOGIN_ENDPOINT = "https://ssb.uc.cl/ERPUC/twbkwbis.P_WWWLogin"
        MENU_ENDPOINT = "https://ssb.uc.cl/ERPUC/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu"

        print('Iniciando driver...', flush=True)
        driver = init_driver()
        print('Driver iniciado!', flush=True)
        # Obtenemos la cookie en base al usuario
        usuario = item.user
        id_usuario = User.objects.get(username=usuario).id
        planner = None
        try:
            print('Obteniendo planner de ' + usuario, flush=True)
            planner = Planner.objects.get(user=id_usuario)
            if planner.estado_toma in {2, 3, 4} or not item.estado:
                driver.quit()
                return (False, 'Planner no disponible o cookie invalida')
        except:
            print('Chequeando que cookie no esta expirada', flush=True)
            if not item.estado:
                print(item.estado, flush=True)
                print('Cookie expirada', flush=True)
                driver.quit()
                return (False, 'Cookie invalida')

        cookie = item.cookie_value
        data[0]["value"] = cookie

        print('Iniciando sesion...', flush=True)
        driver.get(LOGIN_ENDPOINT)

        print('Cargando cookies...', flush=True)
        for cookie in data:
            driver.add_cookie(cookie)
        try:
            print('Chequeando que cookie no esta expirada', flush=True)
            driver.get(MENU_ENDPOINT)
            driver.find_element(by=By.XPATH, value="/html/body/div[3]/table[1]/tbody/tr[1]/td[2]/a")
            print(f'¡Credenciales aceptadas de {usuario}!')
            driver.quit()
            return (True, 'Cuenta aceptada')
        except:
            driver.quit()
            if planner:
                planner.estado_toma = 4
                planner.save()

            cookie = Cookies.objects.get(user=usuario)
            item.estado = False
            item.save()
            print(f'Las credenciales fueron rechazadas. El usuario {usuario} tendrá que hacer login nuevamente', flush=True)
            mail = User.objects.get(username=usuario).email
            send_mail(
            'AutoRamosWeb Necesita ReLogin',
            'Hola, hemos detectado un fallo en tu cuenta y necesitamos que te hagas relogin en el siguiente link: https://autoramos.xyz/relogin/.',
            os.environ.get('EMAIL_HOST_USER'),
            [mail],
            fail_silently=False,
            )
            return (False, 'Cookie invalida')

    threads_ammount = 3
    threads = []
    cookies_master = []
    cant_cookies = Cookies.objects.count()

    for i in range(threads_ammount):
        cookies_master.append(list())
    for id in range(cant_cookies):
        cookies_master[id % threads_ammount].append(Cookies.objects.all()[id])
    print(f"Debug cookies_master: {cookies_master}")
    for cookie_list in cookies_master:
        for cookie in cookie_list:
            t = Thread(target=validate_cookie, args=(cookie,))
            threads.append(t)
            t.start()
    for t in threads:
        t.join()


def scrapeo_img_base64(html, usuario):
    soup = BeautifulSoup(html, 'lxml')
    paso1 = soup.find_all('img')
    img_sucio = paso1[2]['src']

    img = img_sucio.split(',')[-1]

    with open(f"{usuario}.dib","wb") as f:
        f.write(base64.b64decode(img))


def scrapeo_pagina_final(html):
    try:
        print('Scrapeando pagina final...')
        print(f"Debug, html: {html[40]}")
        nrcs = []
        bs = BeautifulSoup(html, 'lxml')
        table = bs.find('table', attrs={'summary':'Esta tabla es usada para presentar Errores de Inscripción.'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            if row.find('th'):
                continue
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            nrc = cols[1]
            nrcs.append(nrc)
        print("SCRAPEO RETORNANDO NRCS: ", nrcs)
        return nrcs
    except Exception as err:
        print("SCRAPEO LLEGO A EXCEPT NO RETORNA NIUNA WEA", err)
        return []
