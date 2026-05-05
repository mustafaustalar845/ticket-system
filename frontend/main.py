from nicegui import ui, app
import httpx
import asyncio
import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api")

ui.add_head_html("""
    <style>
        @media print {
            body * { visibility: hidden; }
            .print-area, .print-area * { visibility: visible; }
            .print-area { position: absolute; left: 0; top: 0; width: 100%; margin: 0; padding: 0; }
            .no-print { display: none !important; }
        }
        .glow-text {
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
            transition: color 0.5s ease, text-shadow 0.5s ease;
        }
        .monitor-bg {
            background: radial-gradient(circle at center, #2d3748 0%, #1a202c 100%);
        }
    </style>
""", shared=True)


async def login(username, password):
    async with httpx.AsyncClient() as client:
        try:
            # OAuth2 expects form-encoded data
            response = await client.post(f"{API_BASE_URL}/auth/login", data={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                app.storage.user['token'] = data.get("access_token")
                ui.notify("Login successful!", type="positive")
                ui.open("/admin")
            else:
                ui.notify("Login failed!", type="negative")
        except Exception as e:
            ui.notify(f"Error connecting to server: {e}", type="negative")

async def take_ticket(tckn):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/tickets/take", json={"tckn": tckn})
            if response.status_code == 200:
                data = response.json()
                ui.notify(f"Ticket Taken: {data['ticket_number']}", type="positive")
                
                with ui.dialog() as dialog, ui.card().classes('print-area flex flex-col items-center p-8 bg-white text-black'):
                    ui.label("Q-MAT TICKETING").classes('text-2xl font-bold mb-4')
                    ui.label("Your Ticket Number").classes('text-lg')
                    ui.label(data['ticket_number']).classes('text-6xl font-extrabold my-4')
                    ui.label("Please wait for your number to be called.").classes('text-sm text-gray-500 mb-6')
                    
                    with ui.row().classes('no-print'):
                        ui.button('Print', on_click=lambda: ui.run_javascript('window.print()')).classes('bg-blue-500 text-white mr-2')
                        ui.button('Close', on_click=dialog.close).classes('bg-gray-500 text-white')
                dialog.open()
            else:
                ui.notify(f"Error: {response.json()}", type="negative")
        except Exception as e:
            ui.notify(f"Error connecting to server: {e}", type="negative")

async def call_next_ticket():
    token = app.storage.user.get('token')
    if not token:
        ui.notify("Not logged in!", type="negative")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/tickets/call_next", headers=headers)
            if response.status_code == 200:
                data = response.json()
                ui.notify(f"Called Ticket: {data['ticket_number']}", type="positive")
            else:
                ui.notify(f"Error: {response.json()}", type="warning")
        except Exception as e:
            ui.notify(f"Error connecting to server: {e}", type="negative")


@ui.page('/')
def index():
    with ui.column().classes('w-full items-center mt-10'):
        ui.label('Ticket Kiosk').classes('text-3xl font-bold mb-5')
        
        tckn_input = ui.input('Enter 11-digit TCKN').classes('w-64')
        ui.button('Take Ticket', on_click=lambda: take_ticket(tckn_input.value)).classes('w-64 mt-2 bg-blue-500 text-white')
        
        ui.link('Staff Login', '/login').classes('mt-10')

@ui.page('/login')
def login_page():
    with ui.column().classes('w-full items-center mt-10'):
        ui.label('Staff Login').classes('text-3xl font-bold mb-5')
        username_input = ui.input('Username').classes('w-64')
        password_input = ui.input('Password', password=True).classes('w-64')
        ui.button('Login', on_click=lambda: login(username_input.value, password_input.value)).classes('w-64 mt-2 bg-green-500 text-white')

@ui.page('/admin')
def admin_page():
    if not app.storage.user.get('token'):
        return ui.navigate.to('/login')

    with ui.column().classes('w-full items-center mt-10'):
        ui.label('Staff Dashboard').classes('text-3xl font-bold mb-5')
        ui.button('Call Next Ticket', on_click=call_next_ticket).classes('w-64 py-4 text-xl bg-orange-500 text-white')
        
        def logout():
            app.storage.user['token'] = None
            ui.navigate.to('/')
        ui.button('Logout', on_click=logout).classes('w-64 mt-5 bg-gray-500 text-white')

@ui.page('/monitor')
def monitor_page():
    with ui.column().classes('w-full h-screen items-center justify-center monitor-bg text-white m-0 p-0 overflow-hidden').style('position: absolute; top: 0; left: 0;'):
        ui.label('NOW SERVING').classes('text-5xl font-bold text-gray-400 tracking-[0.2em] mb-8')
        
        current_ticket = ui.label('---').classes('text-[15rem] font-extrabold text-white leading-none mb-12 glow-text')
        current_ticket.props('id="current-ticket"')
        
        ui.html("""
            <script>
                const host = window.location.hostname;
                const ws = new WebSocket("ws://" + host + ":8000/ws/monitor");
                ws.onmessage = function(event) {
                    const el = document.getElementById("current-ticket");
                    if (el) {
                        let data = event.data;
                        try {
                            const parsed = JSON.parse(event.data);
                            data = parsed.ticket_number || event.data;
                        } catch (e) {
                            // If it's not JSON, use raw text
                        }
                        el.innerText = data;
                        el.style.color = '#4ade80';
                        el.style.textShadow = '0 0 40px rgba(74, 222, 128, 0.8)';
                        setTimeout(() => {
                            el.style.color = 'white';
                            el.style.textShadow = '0 0 20px rgba(255, 255, 255, 0.5)';
                        }, 2000);
                    }
                };
            </script>
        """)

# NiceGUI setup requires a secret to use sessions (app.storage.user)
ui.run(title="Ticket System", host="0.0.0.0", port=8080, storage_secret="my-super-secret-key")
